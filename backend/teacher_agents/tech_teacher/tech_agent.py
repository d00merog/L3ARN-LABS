from ...ai_models.claude_integration import ClaudeAPI

class TechTeacherAgent:
    def __init__(self):
        self.claude_api = ClaudeAPI()

    async def explain_tech_concept(self, concept: str):
        prompt = f"Explain the technology concept of {concept} in simple terms."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def generate_coding_challenge(self, language: str, difficulty: str):
        prompt = f"Generate a {difficulty} coding challenge in {language}."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def provide_tech_trend_insight(self, trend: str):
        prompt = f"Provide insights on the current technology trend: {trend}"
        response = await self.claude_api.generate_response(prompt)
        return response