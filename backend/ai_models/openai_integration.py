import openai
import logging
from ..core.config.settings import settings

logger = logging.getLogger(__name__)

class OpenAIAPI:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def generate_response(self, prompt: str, max_tokens: int = 300) -> str:
        try:
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise ValueError(f"An error occurred while generating the response: {str(e)}")

    async def get_model_info(self) -> dict:
        return {
            "model_name": "gpt-4",
            "model_type": "chat_completion",
            "max_tokens": 8192
        }
