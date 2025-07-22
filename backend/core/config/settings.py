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
    
    # LiteLLM Configuration
    API_KEY_ENCRYPTION_KEY: str = Field(default_factory=lambda: get_secret("API_KEY_ENCRYPTION_KEY"))
    LITELLM_MAX_REQUESTS_PER_MINUTE: int = Field(default=100)
    LITELLM_DEFAULT_TIMEOUT: int = Field(default=30)
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default_factory=lambda: get_secret("CELERY_BROKER_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND: str = Field(default_factory=lambda: get_secret("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"))
    
    # SMTP Configuration for feedback bot
    SMTP_HOST: str = Field(default_factory=lambda: get_secret("SMTP_HOST", "localhost"))
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default_factory=lambda: get_secret("SMTP_USER", ""))
    SMTP_PASSWORD: str = Field(default_factory=lambda: get_secret("SMTP_PASSWORD", ""))
    
    # Bittensor Configuration
    BITTENSOR_NETWORK: str = Field(default="mainnet")  # mainnet, testnet, local
    BITTENSOR_WALLET_NAME: str = Field(default="default")
    BITTENSOR_WALLET_HOTKEY: str = Field(default="default")
    BITTENSOR_QUERY_TIMEOUT: int = Field(default=30)
    BITTENSOR_MAX_MINERS_PER_QUERY: int = Field(default=20)
    BITTENSOR_VALIDATION_THRESHOLD: float = Field(default=0.7)
    BITTENSOR_TAO_REWARD_MULTIPLIER: float = Field(default=1.0)
    
    # WebVM Configuration
    WEBVM_MAX_INSTANCES_PER_USER: int = Field(default=5)
    WEBVM_MAX_SESSION_DURATION_HOURS: int = Field(default=24)
    WEBVM_DEFAULT_RESOURCE_QUOTA_MB: int = Field(default=1024)
    WEBVM_ENABLE_GPU_ACCELERATION: bool = Field(default=True)
    WEBVM_ENABLE_NETWORKING: bool = Field(default=False)
    WEBVM_ENABLE_COLLABORATION: bool = Field(default=True)
    WEBVM_EXECUTION_TIMEOUT_SECONDS: int = Field(default=30)
    WEBVM_FILE_SIZE_LIMIT_MB: int = Field(default=10)
    CHEERPX_LICENSE_KEY: str = Field(default_factory=lambda: get_secret("CHEERPX_LICENSE_KEY", ""))
    WEBASSEMBLY_SIMD_SUPPORT: bool = Field(default=True)

    class Config:
        case_sensitive = True

settings = Settings()
