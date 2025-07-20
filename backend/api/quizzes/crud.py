from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from . import models

async def create_user_answer(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    question: str,
    given_answer: str,
    is_correct: bool,
):
    answer = models.UserAnswer(
        user_id=user_id,
        lesson_id=lesson_id,
        question=question,
        given_answer=given_answer,
        is_correct=is_correct,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer

async def get_top_wrong_answers(db: AsyncSession, lesson_id: int, limit: int = 3):
    result = await db.execute(
        select(models.UserAnswer.question, func.count(models.UserAnswer.id).label("cnt"))
        .where(models.UserAnswer.lesson_id == lesson_id)
        .where(models.UserAnswer.is_correct == False)
        .group_by(models.UserAnswer.question)
        .order_by(func.count(models.UserAnswer.id).desc())
        .limit(limit)
    )
    return result.all()
