from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.courses.models import Course, Lesson
from backend.api.users.models import User
from typing import List

async def generate_learning_path(db: AsyncSession, user_id: int, course_id: int) -> List[int]:
    user = await db.execute(select(User).filter(User.id == user_id))
    user = user.scalar_one()

    course = await db.execute(select(Course).filter(Course.id == course_id))
    course = course.scalar_one()

    lessons = await db.execute(select(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.id))
    lessons = lessons.scalars().all()

    # Implement your adaptive learning algorithm here
    # For now, we'll return a simple linear path
    return [lesson.id for lesson in lessons]
