from pydantic_settings import BaseSettings
from pydantic import Field
from .secrets import get_secret

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default_factory=lambda: get_secret("DATABASE_URL", "sqlite:///./sql_app.db"))
    SECRET_KEY: str = Field(default_factory=lambda: get_secret("SECRET_KEY"))
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    BRAVE_SEARCH_API_KEY: str = Field(default_factory=lambda: get_secret("BRAVE_SEARCH_API_KEY"))
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "production"

    class Config:
        case_sensitive = True

settings = Settings()
