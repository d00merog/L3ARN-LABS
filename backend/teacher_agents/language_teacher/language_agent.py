from ...ai_models.claude_integration import ClaudeAPI

class LanguageTeacherAgent:
    def __init__(self):
        self.claude_api = ClaudeAPI()

    async def generate_grammar_exercise(self, language: str, difficulty: str):
        prompt = f"Generate a {difficulty} grammar exercise for {language} learners."
        response = await self.claude_api.generate_response(prompt)
        return response

    async def provide_translation(self, text: str, from_lang: str, to_lang: str):
        prompt = f"Translate the following text from {from_lang} to {to_lang}: {text}"
        response = await self.claude_api.generate_response(prompt)
        return response

    async def explain_idiom(self, idiom: str, language: str):
        prompt = f"Explain the meaning and usage of the {language} idiom: '{idiom}'"
        response = await self.claude_api.generate_response(prompt)
        return response