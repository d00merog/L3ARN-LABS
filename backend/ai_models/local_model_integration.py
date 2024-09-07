from transformers import pipeline

class LocalModelAPI:
    def __init__(self, model_path: str):
        self.generator = pipeline('text-generation', model=model_path)

    async def generate_response(self, prompt: str) -> str:
        response = self.generator(prompt, max_length=150, num_return_sequences=1)
        return response[0]['generated_text']