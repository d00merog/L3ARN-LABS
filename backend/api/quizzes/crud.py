from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..courses.models import Lesson, Course
from ..gradebook import crud as gradebook_crud, schemas as gradebook_schemas

async def get_lesson_with_course(db: AsyncSession, lesson_id: int):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        return None, None
    course_result = await db.execute(select(Course).where(Course.id == lesson.course_id))
    course = course_result.scalar_one_or_none()
    return lesson, course

async def save_quiz_result(db: AsyncSession, user_id: int, lesson_id: int, score: float):
    data = gradebook_schemas.QuizResultCreate(user_id=user_id, lesson_id=lesson_id, score=score)
    return await gradebook_crud.create_quiz_result(db, data)
