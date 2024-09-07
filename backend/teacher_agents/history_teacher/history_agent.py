from ...ai_models.claude_integration import ClaudeAPI

class HistoryTeacherAgent:
    def __init__(self):
        self.claude_api = ClaudeAPI()

    async def generate_history_question(self, era: str, difficulty: str):
        prompt = f"Generate a {difficulty} history question about the {era}."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def provide_historical_context(self, event: str):
        prompt = f"Provide historical context for the event: {event}."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def compare_historical_periods(self, period1: str, period2: str):
        prompt = f"Compare and contrast the historical periods: {period1} and {period2}."
        response = await self.claude_api.generate_response(prompt)
        return response