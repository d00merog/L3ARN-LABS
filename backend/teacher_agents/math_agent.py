from .base_agent import BaseTeacherAgent

class MathTeacher(BaseTeacherAgent):
    def __init__(self, model: str):
        super().__init__(model)

    async def generate_lesson(self, topic: str, difficulty: str) -> str:
        prompt = f"Create a math lesson about {topic} at {difficulty} level."
        return await self.generate_content(prompt)

    async def generate_quiz(self, lesson_content: str) -> str:
        prompt = f"Based on the following math lesson, create a quiz:\n\n{lesson_content}"
        return await self.generate_content(prompt)

    async def grade_answer(self, question: str, student_answer: str, correct_answer: str) -> float:
        prompt = f"Grade the following answer to a math question:\nQuestion: {question}\nStudent's Answer: {student_answer}\nCorrect Answer: {correct_answer}"
        grade_response = await self.generate_content(prompt)
        return self.parse_grade(grade_response)

    async def provide_step_by_step_solution(self, problem: str) -> str:
        prompt = f"Provide a step-by-step solution for the following math problem:\n{problem}"
        return await self.generate_content(prompt)
