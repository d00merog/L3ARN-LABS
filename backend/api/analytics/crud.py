from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..courses.models import Lesson, Course
from ..gradebook.models import QuizResult

async def get_instructor_analytics(db: AsyncSession, instructor_id: int):
    result = await db.execute(
        select(
            Lesson.id.label("lesson_id"),
            Lesson.title.label("lesson_title"),
            func.coalesce(func.avg(QuizResult.score), 0).label("avg_score"),
            func.count(QuizResult.id).label("attempts"),
            func.max(QuizResult.taken_at).label("last_activity"),
        )
        .select_from(Lesson)
        .join(Course, Lesson.course_id == Course.id)
        .outerjoin(QuizResult, QuizResult.lesson_id == Lesson.id)
        .where(Course.instructor_id == instructor_id)
        .group_by(Lesson.id)
    )
    rows = result.all()
    return [
        {
            "lesson_id": r.lesson_id,
            "lesson_title": r.lesson_title,
            "avg_score": float(r.avg_score) if r.avg_score is not None else 0.0,
            "attempts": r.attempts,
            "last_activity": r.last_activity,
        }
        for r in rows
    ]

async def get_course_analytics(db: AsyncSession, course_id: int):
    result = await db.execute(
        select(
            Lesson.id.label("lesson_id"),
            func.coalesce(func.avg(QuizResult.score), 0).label("avg_score"),
            func.count(QuizResult.id).label("attempts"),
        )
        .select_from(Lesson)
        .outerjoin(QuizResult, QuizResult.lesson_id == Lesson.id)
        .where(Lesson.course_id == course_id)
        .group_by(Lesson.id)
    )
    rows = result.all()
    avg_score = 0.0
    attempts = 0
    if rows:
        total_score = sum(float(r.avg_score or 0) for r in rows)
        avg_score = total_score / len(rows)
        attempts = sum(r.attempts for r in rows)
    return {
        "course_id": course_id,
        "avg_score": avg_score,
        "attempts": attempts,
    }
