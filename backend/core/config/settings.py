import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BRAVE_SEARCH_API_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "production"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
