from abc import ABC, abstractmethod
from ..ai_models.model_selector import ModelSelector

class BaseTeacherAgent(ABC):
    def __init__(self, model: str):
        self.model = ModelSelector.get_model(model)

    @abstractmethod
    async def generate_lesson(self, topic: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_quiz(self, lesson_content: str) -> str:
        pass

    @abstractmethod
    async def grade_answer(self, question: str, student_answer: str, correct_answer: str) -> float:
        pass

    async def generate_content(self, prompt: str) -> str:
        return await self.model.generate_response(prompt)

    def parse_grade(self, grade_response: str) -> float:
        # Implement logic to parse the grade from the AI response
        # This is a simple implementation and might need to be adjusted based on the AI's output format
        try:
            return float(grade_response.strip().split()[0])
        except ValueError:
            return 0.0
