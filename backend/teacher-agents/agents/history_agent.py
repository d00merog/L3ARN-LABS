from ..ai_models.model_selector import ModelSelector
from ..utils import brave_search, web_scraper, text_to_speech
from .base_agent import BaseTeacherAgent

class HistoryTeacher(BaseTeacherAgent):
    def __init__(self, model: str):
        super().__init__(model)

    async def generate_lesson(self, topic: str, era: str) -> str:
        prompt = f"Create a history lesson about {topic} from the {era} era."
        return await self.generate_content(prompt)

    async def generate_quiz(self, lesson_content: str) -> str:
        prompt = f"Based on the following history lesson, create a quiz:\n\n{lesson_content}"
        return await self.generate_content(prompt)

    async def grade_answer(self, question: str, student_answer: str, correct_answer: str) -> float:
        prompt = f"Grade the following answer to a history question:\nQuestion: {question}\nStudent's Answer: {student_answer}\nCorrect Answer: {correct_answer}"
        grade_response = await self.generate_content(prompt)
        return self.parse_grade(grade_response)

    async def provide_historical_context(self, event: str, era: str) -> str:
        prompt = f"Provide historical context for the event '{event}' during the {era} era."
        context = await self.generate_content(prompt)
        additional_info = await brave_search.search_missing_info(f"{event} {era}")
        full_context = f"{context}\n\nAdditional information:\n{additional_info}"
        return full_context

    async def create_audio_lesson(self, topic: str, era: str) -> str:
        lesson = await self.generate_lesson(topic, era)
        audio_file = await text_to_speech.generate_audio(lesson, "en")
        return audio_file
