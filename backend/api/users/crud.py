from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional, Any
from . import models, schemas
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from ...core.security import verify_password, get_password_hash
from ..auth.crud import create_tokens
from datetime import timedelta
from ...core.config.settings import settings
from fastapi import HTTPException

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

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=getattr(user, "username", None),
        role=user.role.value if hasattr(user, "role") else models.UserRole.STUDENT.value,
    )
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

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def create_user_token(db: AsyncSession, user: schemas.User):
    return await create_tokens(db, user)

async def get_user_by_address(db: AsyncSession, address: str):
    result = await db.execute(select(models.User).filter(models.User.web3_address == address))
    return result.scalar_one_or_none()

async def create_user_from_address(db: AsyncSession, address: str):
    user = models.User(username=f"user_{address[:8]}", email=f"{address[:8]}@example.com", web3_address=address)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

class ProfileManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user_profile(self, user_id: int, new_data: Dict[str, Any]) -> Dict[str, Any]:
        user = await get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for key, value in new_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
        
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return user.dict()

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        user = await get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.dict()
