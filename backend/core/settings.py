"""
Unified application settings with environment variable configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field
import os
import logging
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "L3ARN-LABS AI-Powered Learning Platform"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = Field(description="JWT secret key for token generation")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field(description="Database connection URL")
    SQL_DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost",
        "https://l3arn-labs.com",
    ]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    
    # External APIs
    BRAVE_SEARCH_API_KEY: Optional[str] = None
    
    # Payment Integration
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_BASIC_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_SUCCESS_URL: str = "http://localhost:3000/success"
    STRIPE_CANCEL_URL: str = "http://localhost:3000/cancel"
    
    # AI Models
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # External Services
    WEB3_PROVIDER_URL: Optional[str] = None

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
