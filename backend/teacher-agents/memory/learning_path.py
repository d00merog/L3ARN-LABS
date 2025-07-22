from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.courses.models import Course, Lesson
from backend.api.users.models import User
from backend.api.lessons import crud as lesson_crud
from typing import List, Dict
from fastapi import HTTPException
from ..utils import web_scraper, text_to_speech, speech_recognition
from ..ai_models.model_selector import ModelSelector

class AdaptiveLearningPath:
    def __init__(self):
        self.db: AsyncSession = None
        self.language_data_collector = None
        self.model = ModelSelector.get_model("gpt-3.5-turbo")

    async def generate_learning_path(self, user_id: int, course_id: int) -> Dict[str, any]:
        user = await self.db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        course = await self.db.execute(select(Course).filter(Course.id == course_id))
        course = course.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        language_data = await self.language_data_collector.collect_user_language_data(user_id)
        completed_lessons = await lesson_crud.get_completed_user_lessons(self.db, user_id)
        
        all_lessons = await self.db.execute(select(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.id))
        all_lessons = all_lessons.scalars().all()
        
        available_lessons = [lesson for lesson in all_lessons if lesson not in completed_lessons]
        sorted_lessons = self._sort_lessons_by_relevance(available_lessons, language_data)
        
        recommended_lessons = sorted_lessons[:5]  # Recommend top 5 lessons

        return {
            "user_id": user_id,
            "course_id": course_id,
            "recommended_lessons": [{"id": lesson.id, "title": lesson.title} for lesson in recommended_lessons]
        }

    def _sort_lessons_by_relevance(self, lessons: List[Lesson], language_data: Dict[str, float]) -> List[Lesson]:
        def lesson_relevance(lesson):
            return -abs(lesson.difficulty - language_data['proficiency_estimate'])

        return sorted(lessons, key=lesson_relevance)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            await self.db.close()

    async def generate_resource(self, topic: str):
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        content = await web_scraper.scrape_webpage(url)
        summary = await self.model.generate_response(f"Summarize this content: {content[:1000]}")
        audio = await text_to_speech.generate_audio(summary, "en")
        return {"summary": summary, "audio": audio}

    async def process_voice_input(self, audio_file: str):
        transcription = await speech_recognition.transcribe_audio(audio_file, "en")
        response = await self.model.generate_response(f"Respond to this input: {transcription}")
        return response
