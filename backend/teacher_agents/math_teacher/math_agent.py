from ...ai_models.model_selector import ModelSelector
from ...utils.brave_search import search_missing_info

class MathTeacherAgent:
    def __init__(self, model_name: str = "claude"):
        self.ai_model = ModelSelector.get_model(model_name)

    async def generate_math_problem(self, difficulty: str, topic: str):
        prompt = f"Generate a {difficulty} math problem about {topic}."
        response = await self.ai_model.generate_response(prompt)
        if not response or "I don't have enough information" in response:
            additional_info = await search_missing_info(topic)
            prompt += f"\n\nAdditional context: {additional_info}"
            response = await self.ai_model.generate_response(prompt)
        return response

    async def check_solution(self, problem: str, student_solution: str):
        prompt = f"Problem: {problem}\nStudent's solution: {student_solution}\nIs this solution correct? Explain why or why not."
        response = await self.ai_model.generate_response(prompt)
        return response

    async def provide_hint(self, problem: str):
        prompt = f"For the math problem: {problem}\nProvide a helpful hint without giving away the full solution."
        response = await self.ai_model.generate_response(prompt)
        return response