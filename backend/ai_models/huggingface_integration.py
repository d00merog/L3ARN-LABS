from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    def __init__(self, model_name: str = 'gpt2'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)

    async def generate_response(self, prompt: str, max_length: int = 300, num_return_sequences: int = 1) -> List[Dict[str, Any]]:
        try:
            response = await asyncio.to_thread(
                self.generator,
                prompt,
                max_length=max_length,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            return response
        except Exception as e:
            logger.error(f"HuggingFace API error: {str(e)}")
            raise ValueError(f"An error occurred while generating the response: {str(e)}")

    async def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model.config.name_or_path,
            "model_type": self.model.config.model_type,
            "vocab_size": self.model.config.vocab_size,
            "max_position_embeddings": self.model.config.max_position_embeddings
        }
