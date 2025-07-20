"""
Application settings with environment variable configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field
import os
from ..config.secrets import get_secret
import logging
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "L3ARN-LABS"
    VERSION: str = "0.1.0"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: get_secret("JWT_SECRET_KEY", "your_jwt_secret_key_here"))
    ALGORITHM: str = Field(default_factory=lambda: get_secret("JWT_ALGORITHM", "HS256"))

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default_factory=lambda: int(get_secret("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    
    # Database
    DATABASE_URL: str = Field(default_factory=lambda: get_secret("DATABASE_URL", "postgresql://user:password@localhost:5432/l3arn_labs"))
    SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() == "true"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(get_secret("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: get_secret("DATABASE_URL", "postgresql://user:password@localhost:5432/l3arn_labs")
    )
    SQL_DEBUG: bool = get_secret("SQL_DEBUG", "false").lower() == "true"


    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "https://l3arn-labs.com",
    ]

    # Logging
    LOG_LEVEL: str = get_secret("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Cache
    REDIS_URL: Optional[str] = get_secret("REDIS_URL")
    CACHE_TTL: int = int(get_secret("CACHE_TTL", "3600"))

    # File Storage
    UPLOAD_DIR: str = get_secret("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(get_secret("MAX_UPLOAD_SIZE", "5242880"))  # 5MB

    class Config:
        """Pydantic config"""
        case_sensitive = True

        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance"""
    return Settings()

# Initialize settings
settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
