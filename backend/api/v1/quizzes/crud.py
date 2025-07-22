from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .models import QuizResult

async def create_quiz_result(db: AsyncSession, user_id: int, lesson_id: int, score: int, answers: list) -> QuizResult:
    quiz = QuizResult(user_id=user_id, lesson_id=lesson_id, score=score, answers=answers)
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    return quiz

async def get_results_by_lesson(db: AsyncSession, lesson_id: int) -> List[QuizResult]:
    results = await db.execute(select(QuizResult).filter(QuizResult.lesson_id == lesson_id))
    return results.scalars().all()
