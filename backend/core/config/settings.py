from pydantic_settings import BaseSettings
from pydantic import Field
from .secrets import get_secret

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default_factory=lambda: get_secret("DATABASE_URL", "sqlite:///./sql_app.db"))
    SECRET_KEY: str = Field(default_factory=lambda: get_secret("SECRET_KEY"))
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    BRAVE_SEARCH_API_KEY: str = Field(default_factory=lambda: get_secret("BRAVE_SEARCH_API_KEY"))
    STRIPE_API_KEY: str = Field(default_factory=lambda: get_secret("STRIPE_API_KEY"))
    STRIPE_WEBHOOK_SECRET: str = Field(default_factory=lambda: get_secret("STRIPE_WEBHOOK_SECRET"))
    STRIPE_BASIC_PRICE_ID: str = Field(default_factory=lambda: get_secret("STRIPE_BASIC_PRICE_ID", ""))
    STRIPE_PRO_PRICE_ID: str = Field(default_factory=lambda: get_secret("STRIPE_PRO_PRICE_ID", ""))
    STRIPE_SUCCESS_URL: str = Field(default_factory=lambda: get_secret("STRIPE_SUCCESS_URL", "http://localhost:3000/success"))
    STRIPE_CANCEL_URL: str = Field(default_factory=lambda: get_secret("STRIPE_CANCEL_URL", "http://localhost:3000/cancel"))
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "production"

    class Config:
        case_sensitive = True

settings = Settings()
