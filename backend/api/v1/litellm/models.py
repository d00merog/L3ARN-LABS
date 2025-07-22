"""
LiteLLM Integration Models
Community-powered AI model access with API key donations
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ...core.database import Base


class APIKeyProvider(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"
    AZURE = "azure"
    BEDROCK = "bedrock"


class APIKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class DonatedAPIKey(Base):
    """Stores community-donated API keys for shared AI model access"""
    __tablename__ = "donated_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    donor_user_id = Column(Integer, index=True)
    provider = Column(Enum(APIKeyProvider), nullable=False)
    key_hash = Column(String, nullable=False, unique=True)  # Hashed for security
    encrypted_key = Column(Text, nullable=False)  # Encrypted actual key
    nickname = Column(String(100))  # Optional friendly name
    monthly_limit = Column(Float, default=0.0)  # USD limit per month
    usage_this_month = Column(Float, default=0.0)
    total_usage = Column(Float, default=0.0)
    status = Column(Enum(APIKeyStatus), default=APIKeyStatus.ACTIVE)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    usage_records = relationship("APIKeyUsage", back_populates="api_key")


class APIKeyUsage(Base):
    """Tracks usage of donated API keys"""
    __tablename__ = "api_key_usage"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    model_name = Column(String(100), nullable=False)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    request_type = Column(String(50))  # completion, embedding, image, etc.
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    api_key = relationship("DonatedAPIKey", back_populates="usage_records")


class UserContribution(Base):
    """Tracks user contributions and credits"""
    __tablename__ = "user_contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    total_donated_usd = Column(Float, default=0.0)
    credits_earned = Column(Float, default=0.0)
    credits_used = Column(Float, default=0.0)
    credits_remaining = Column(Float, default=0.0)
    contribution_tier = Column(String(20), default="basic")  # basic, supporter, patron, benefactor
    monthly_usage_limit = Column(Float, default=5.0)  # USD per month
    priority_level = Column(Integer, default=1)  # Higher number = higher priority
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ModelLoadBalancer(Base):
    """Load balancer configuration for AI models"""
    __tablename__ = "model_load_balancer"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False)
    provider_weights = Column(JSON)  # {"openai": 0.4, "anthropic": 0.3, "google": 0.3}
    fallback_order = Column(JSON)  # ["openai", "anthropic", "google"]
    enabled = Column(Boolean, default=True)
    min_healthy_keys = Column(Integer, default=1)
    health_check_interval = Column(Integer, default=300)  # seconds
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AIModelRequest(Base):
    """Log of all AI model requests for analytics"""
    __tablename__ = "ai_model_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(100), index=True)
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    api_key_id = Column(Integer, index=True)
    request_type = Column(String(50))  # chat, completion, embedding, image
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost_usd = Column(Float)
    response_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_code = Column(String(50))
    error_message = Column(Text)
    user_agent = Column(String(200))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())


class AIModelHealth(Base):
    """Health monitoring for AI models and providers"""
    __tablename__ = "ai_model_health"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(Enum(APIKeyProvider), nullable=False)
    model_name = Column(String(100), nullable=False)
    status = Column(String(20), default="healthy")  # healthy, degraded, down
    response_time_avg = Column(Float)  # Average response time in ms
    success_rate = Column(Float)  # Success rate 0.0 to 1.0
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    last_check = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Index optimizations
from sqlalchemy import Index

# Add indexes for better query performance
Index('idx_donated_keys_provider_status', DonatedAPIKey.provider, DonatedAPIKey.status)
Index('idx_usage_user_date', APIKeyUsage.user_id, APIKeyUsage.created_at)
Index('idx_requests_user_date', AIModelRequest.user_id, AIModelRequest.created_at)
Index('idx_health_provider_model', AIModelHealth.provider, AIModelHealth.model_name)