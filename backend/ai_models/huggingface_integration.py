from transformers import pipeline
from ..core.config.settings import settings

class HuggingFaceAPI:
    def __init__(self):
        self.generator = pipeline('text-generation', model='gpt2')

    async def generate_response(self, prompt: str) -> str:
        response = self.generator(prompt, max_length=150, num_return_sequences=1)
        return response[0]['generated_text']