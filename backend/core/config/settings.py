import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sql_app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Model configurations
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY")
    LOCAL_MODEL_PATH: str = os.getenv("LOCAL_MODEL_PATH", "")

    BRAVE_SEARCH_API_KEY: str = os.getenv("BRAVE_SEARCH_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
