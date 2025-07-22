from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...api.users.models import User
from ...api.courses.models import Course, Lesson
from ...ml.recommendation_model import RecommendationModel

class AdaptiveLearningPath:
    def __init__(self):
        self.recommendation_model = RecommendationModel()

    async def generate_learning_path(self, user_id: int, course_id: int, db: AsyncSession):
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        course = await db.execute(select(Course).filter(Course.id == course_id))
        course = course.scalar_one_or_none()
        if not course:
            raise ValueError(f"Course with id {course_id} not found")

        # Get personalized recommendations
        recommendations = await self.recommendation_model.get_recommendations(user_id, db)

        # Filter recommendations for the current course
        course_recommendations = [rec for rec in recommendations if rec["course_id"] == course_id]

        # If no recommendations for the current course, fall back to default order
        if not course_recommendations:
            lessons = await db.execute(select(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order))
            lessons = lessons.scalars().all()
        else:
            # Use recommended lessons
            lesson_ids = [rec["course_id"] for rec in course_recommendations]
            lessons = await db.execute(select(Lesson).filter(Lesson.id.in_(lesson_ids)))
            lessons = lessons.scalars().all()
            # Sort lessons based on recommendation order
            lessons.sort(key=lambda l: lesson_ids.index(l.id))

        # Create learning path
        learning_path = []
        for lesson in lessons:
            learning_path.append({
                "lesson_id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "content": lesson.content,
                "order": lesson.order,
                "difficulty": lesson.difficulty
            })

        return {
            "user_id": user_id,
            "course_id": course_id,
            "course_title": course.title,
            "learning_path": learning_path
        }

    async def update_user_progress(self, user_id: int, lesson_id: int, completed: bool, db: AsyncSession):
        # Update user progress and trigger model retraining if necessary
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        lesson = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
        lesson = lesson.scalar_one_or_none()
        if not lesson:
            raise ValueError(f"Lesson with id {lesson_id} not found")

        # Update user progress (you may need to create a UserProgress model)
        # For simplicity, we'll just update the user's completed_lessons field
        if completed:
            user.completed_lessons.append(lesson_id)
        else:
            user.completed_lessons.remove(lesson_id)

        await db.commit()

        # Retrain the recommendation model periodically (e.g., every 10 completed lessons)
        if len(user.completed_lessons) % 10 == 0:
            await self.recommendation_model.train(db)

        return {"message": "User progress updated successfully"}
