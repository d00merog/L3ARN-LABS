import asyncio
from ...core.database import SessionLocal
from ...api.users import crud as user_crud
from ...api.courses import crud as course_crud
from ...api.lessons import crud as lesson_crud
from ...models.language_data import LanguageData
from sqlalchemy.orm import Session
import random

class LanguageDataCollector:
    def __init__(self):
        self.db = SessionLocal()

    async def collect_user_language_data(self, user_id: int):
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        # Collect user's course data
        user_courses = course_crud.get_user_courses(self.db, user_id)
        
        # Collect user's lesson data
        user_lessons = lesson_crud.get_user_lessons(self.db, user_id)
        
        # Simulate collecting language samples (e.g., from user's written responses or audio recordings)
        language_samples = await self._simulate_language_sample_collection(user_lessons)
        
        # Calculate interaction count based on completed lessons
        interaction_count = len([lesson for lesson in user_lessons if lesson.is_completed])
        
        # Estimate proficiency based on course progress and lesson performance
        proficiency_estimate = self._estimate_proficiency(user_courses, user_lessons)
        
        language_data = {
            "user_id": user_id,
            "language_samples": language_samples,
            "interaction_count": interaction_count,
            "proficiency_estimate": proficiency_estimate
        }
        
        # Save the collected data to the database
        self._save_language_data(self.db, language_data)
        
        print(f"Collected and saved language data for user {user_id}")
        return language_data

    async def batch_collect_data(self, user_ids: list[int]):
        tasks = [self.collect_user_language_data(user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)

    async def _simulate_language_sample_collection(self, lessons):
        # In a real scenario, this would involve processing actual user input
        await asyncio.sleep(1)  # Simulate processing time
        return [f"Sample from lesson {lesson.id}" for lesson in lessons[:3]]

    def _estimate_proficiency(self, courses, lessons):
        if not courses or not lessons:
            return 0.0
        
        course_completion = sum(course.progress for course in courses) / len(courses)
        lesson_performance = sum(lesson.score for lesson in lessons if lesson.score is not None)
        lesson_performance /= len(lessons) if lessons else 1
        
        return (course_completion * 0.6 + lesson_performance * 0.4)

    def _save_language_data(self, db: Session, data: dict):
        language_data = LanguageData(
            user_id=data["user_id"],
            language_samples=",".join(data["language_samples"]),
            interaction_count=data["interaction_count"],
            proficiency_estimate=data["proficiency_estimate"]
        )
        db.add(language_data)
        db.commit()
        db.refresh(language_data)

    def __del__(self):
        self.db.close()