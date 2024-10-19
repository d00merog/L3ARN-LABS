from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from .models import Course, Enrollment, User
from typing import List
from backend.api import models

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

async def get_recommended_courses(db: AsyncSession, user_id: int, limit: int = 5) -> List[Course]:
    user_enrollments = await db.execute(
        select(Enrollment.course_id).where(Enrollment.user_id == user_id)
    )
    enrolled_course_ids = [enrollment.course_id for enrollment in user_enrollments.scalars().all()]

    user_course_types = await db.execute(
        select(Course.type).where(Course.id.in_(enrolled_course_ids)).distinct()
    )
    user_course_types = [course_type[0] for course_type in user_course_types.scalars().all()]

    recommended_courses = await db.execute(
        select(Course)
        .where(Course.id.notin_(enrolled_course_ids))
        .where(Course.type.in_(user_course_types))
        .order_by(func.random())
        .limit(limit)
    )

    return recommended_courses.scalars().all()
