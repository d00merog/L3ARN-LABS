from .claude_integration import ClaudeAPI
from .openai_integration import OpenAIAPI
from .huggingface_integration import HuggingFaceAPI
from .local_model_integration import LocalModelAPI
from ..core.config.settings import settings

class ModelSelector:
    @staticmethod
    def get_model(model_name: str):
        if model_name == "claude":
            return ClaudeAPI()
        elif model_name == "openai":
            return OpenAIAPI()
        elif model_name == "huggingface":
            return HuggingFaceAPI()
        elif model_name == "local":
            return LocalModelAPI(settings.LOCAL_MODEL_PATH)
        else:
            raise ValueError(f"Unknown model: {model_name}")