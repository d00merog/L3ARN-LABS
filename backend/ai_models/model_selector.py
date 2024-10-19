from .claude_integration import ClaudeAPI
from .openai_integration import OpenAIAPI
from .huggingface_integration import HuggingFaceAPI
from .local_model_integration import LocalModelAPI
from ..core.config.settings import settings

class ModelSelector:
    @staticmethod
    async def get_model(model_name: str):
        model_map = {
            "claude": ClaudeAPI,
            "openai": OpenAIAPI,
            "huggingface": HuggingFaceAPI,
            "local": LocalModelAPI
        }
        
        model_name_lower = model_name.lower()
        model_class = model_map.get(model_name_lower)
        
        if model_class:
            if model_name_lower == "local":
                return await model_class.create(settings.LOCAL_MODEL_PATH)
            return model_class()
        elif model_name_lower.startswith('gpt'):
            return OpenAIAPI()
        elif model_name_lower.startswith('hf'):
            return HuggingFaceAPI(model_name)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
