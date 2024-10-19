import aiohttp
from anthropic import AsyncAnthropic
from ..core.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ClaudeAPI:
    def __init__(self):
        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is not set in the environment variables")
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)

    async def generate_response(self, prompt: str, max_tokens: int = 300) -> str:
        try:
            response = await self.client.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=max_tokens
            )
            return response.completion
        except aiohttp.ClientError as e:
            logger.error(f"Network error while calling Claude API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while calling Claude API: {str(e)}")
            raise
