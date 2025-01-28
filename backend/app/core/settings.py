"""
Application settings with environment variable configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os
import logging
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation"""
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "L3ARN-LABS"
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/l3arn_labs")
    SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "https://l3arn-labs.com"
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))  # 5MB
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance"""
    return Settings()

# Initialize settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
