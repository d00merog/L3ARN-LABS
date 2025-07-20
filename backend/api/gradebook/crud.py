from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas

async def create_quiz_result(db: AsyncSession, result: schemas.QuizResultCreate) -> models.QuizResult:
    db_result = models.QuizResult(**result.dict())
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)
    return db_result

async def get_results_by_user(db: AsyncSession, user_id: int):
    res = await db.execute(select(models.QuizResult).where(models.QuizResult.user_id == user_id))
    return res.scalars().all()

async def get_results_by_lesson(db: AsyncSession, lesson_id: int):
    res = await db.execute(select(models.QuizResult).where(models.QuizResult.lesson_id == lesson_id))
    return res.scalars().all()
