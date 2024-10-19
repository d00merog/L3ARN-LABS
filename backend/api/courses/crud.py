from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_courses(db: Session, skip: int = 0, limit: int = 10, search: str = None, course_type: str = None):
    query = db.query(models.Course)
    if search:
        search = f"%{search}%"
        query = query.filter(or_(
            models.Course.title.ilike(search),
            models.Course.description.ilike(search),
            models.Course.topic.ilike(search)
        ))
    if course_type:
        query = query.filter(models.Course.type == course_type)
    
    total = query.count()
    courses = query.offset(skip).limit(limit).all()
    return courses, total

def create_course(db: Session, course: schemas.CourseCreate, user_id: int, content: str):
    db_course = models.Course(
        **course.dict(),
        user_id=user_id,
        content=content
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def get_course_reviews(db: Session, course_id: int):
    return db.query(models.Review).filter(models.Review.course_id == course_id).all()

def create_course_review(db: Session, review: schemas.ReviewCreate, course_id: int, user_id: int):
    db_review = models.Review(**review.dict(), course_id=course_id, user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def enroll_user_in_course(db: Session, user_id: int, course_id: int):
    course = get_course(db, course_id=course_id)
    if not course:
        return None
    
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user_id,
        models.Enrollment.course_id == course_id
    ).first()
    
    if existing_enrollment:
        return None
    
    new_enrollment = models.Enrollment(user_id=user_id, course_id=course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

class CourseRecommender:
    def __init__(self, courses):
        self.courses = courses
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform([f"{c.title} {c.description} {c.topic}" for c in courses])

    def get_recommendations(self, course_id, num_recommendations=5):
        course_idx = next(i for i, c in enumerate(self.courses) if c.id == course_id)
        cosine_similarities = cosine_similarity(self.tfidf_matrix[course_idx], self.tfidf_matrix).flatten()
        related_course_indices = cosine_similarities.argsort()[-num_recommendations-1:-1][::-1]
        return [self.courses[i] for i in related_course_indices if i != course_idx]

def get_course_recommendations(db: Session, course_id: int, num_recommendations: int = 5):
    courses = db.query(models.Course).all()
    recommender = CourseRecommender(courses)
    return recommender.get_recommendations(course_id, num_recommendations)

async def get_recommended_courses(db: AsyncSession, user_id: int, limit: int = 5) -> List[models.Course]:
    user_enrollments = await db.execute(
        select(models.Enrollment.course_id).where(models.Enrollment.user_id == user_id)
    )
    enrolled_course_ids = [enrollment.course_id for enrollment in user_enrollments.scalars().all()]

    user_course_types = await db.execute(
        select(models.Course.type).where(models.Course.id.in_(enrolled_course_ids)).distinct()
    )
    user_course_types = [course_type[0] for course_type in user_course_types.scalars().all()]

    recommended_courses = await db.execute(
        select(models.Course)
        .where(models.Course.id.notin_(enrolled_course_ids))
        .where(models.Course.type.in_(user_course_types))
        .order_by(func.random())
        .limit(limit)
    )

    return recommended_courses.scalars().all()
