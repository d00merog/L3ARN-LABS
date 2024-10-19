from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LocalModelAPI:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)
        self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer, device=self.device)

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
            logger.error(f"Error generating response: {str(e)}")
            raise ValueError(f"An error occurred while generating the response: {str(e)}")

    @classmethod
    async def create(cls, model_path: str):
        instance = cls(model_path)
        return instance

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model_path='{self.model_path}')"

    async def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model.config.name_or_path,
            "model_type": self.model.config.model_type,
            "vocab_size": self.model.config.vocab_size,
            "max_position_embeddings": self.model.config.max_position_embeddings
        }
