from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
from backend.ai_models import models, schemas
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

async def get_user_course_progress(db: AsyncSession, user_id: int) -> List[Dict[str, float]]:
    try:
        enrollments = await db.execute(
            select(models.Enrollment).filter(models.Enrollment.user_id == user_id)
        )
        enrollments = enrollments.scalars().all()

        progress = []
        for enrollment in enrollments:
            completed_lessons, total_lessons = await db.execute(
                select(
                    func.count(models.LessonCompletion.id).label('completed'),
                    func.count(models.Lesson.id).label('total')
                ).select_from(models.Lesson).outerjoin(
                    models.LessonCompletion,
                    (models.LessonCompletion.lesson_id == models.Lesson.id) &
                    (models.LessonCompletion.user_id == user_id)
                ).filter(models.Lesson.course_id == enrollment.course_id)
            ).first()

            progress_percentage = round((completed_lessons / total_lessons) * 100, 2) if total_lessons > 0 else 0.0

            progress.append({
                "course_id": enrollment.course_id,
                "progress": progress_percentage
            })

        return progress
    except SQLAlchemyError as e:
        await db.rollback()
        raise ValueError(f"Database error occurred: {str(e)}")

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user: models.User, user_update: schemas.UserUpdate) -> models.User:
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user
