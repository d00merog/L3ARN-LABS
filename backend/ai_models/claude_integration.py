import aiohttp
import os

class ClaudeAPI:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/completions"

    async def generate_response(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }
        data = {
            "prompt": prompt,
            "model": "claude-v1",
            "max_tokens_to_sample": 300,
            "temperature": 0.7,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['completion']
                else:
                    raise Exception(f"API request failed with status {response.status}")