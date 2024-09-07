import openai
from ..core.config.settings import settings

class OpenAIAPI:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def generate_response(self, prompt: str) -> str:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()