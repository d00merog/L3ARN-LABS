from ...ai_models.claude_integration import ClaudeAPI

class ScienceTeacherAgent:
    def __init__(self):
        self.claude_api = ClaudeAPI()

    async def generate_science_question(self, topic: str, difficulty: str):
        prompt = f"Generate a {difficulty} science question about {topic}."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def explain_concept(self, concept: str):
        prompt = f"Explain the scientific concept of {concept} in simple terms."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def provide_experiment_idea(self, topic: str):
        prompt = f"Suggest a simple experiment related to {topic} that can be done at home."
        response = await self.claude_api.generate_response(prompt)
        return response