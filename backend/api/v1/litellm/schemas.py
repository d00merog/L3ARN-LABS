"""
LiteLLM Integration Schemas
Pydantic models for API key donation and management
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class APIKeyProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"
    AZURE = "azure"
    BEDROCK = "bedrock"


class APIKeyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class ContributionTier(str, Enum):
    BASIC = "basic"
    SUPPORTER = "supporter"
    PATRON = "patron"
    BENEFACTOR = "benefactor"


# API Key Donation Schemas
class APIKeyDonationCreate(BaseModel):
    provider: APIKeyProvider
    api_key: str = Field(..., min_length=10)
    nickname: Optional[str] = Field(None, max_length=100)
    monthly_limit: float = Field(default=50.0, ge=0, le=1000)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if len(v) < 10:
            raise ValueError('API key too short')
        # Add provider-specific validation here
        return v


class APIKeyDonation(BaseModel):
    id: int
    provider: APIKeyProvider
    nickname: Optional[str]
    monthly_limit: float
    usage_this_month: float
    total_usage: float
    status: APIKeyStatus
    last_used: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyDonationUpdate(BaseModel):
    nickname: Optional[str] = None
    monthly_limit: Optional[float] = Field(None, ge=0, le=1000)
    status: Optional[APIKeyStatus] = None


# User Contribution Schemas
class UserContributionInfo(BaseModel):
    user_id: int
    total_donated_usd: float
    credits_earned: float
    credits_used: float
    credits_remaining: float
    contribution_tier: ContributionTier
    monthly_usage_limit: float
    priority_level: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContributionStats(BaseModel):
    total_contributors: int
    total_donated_usd: float
    active_api_keys: int
    models_available: int
    current_month_usage: float
    success_rate: float


# AI Model Request Schemas
class AIModelRequestCreate(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    user_id: Optional[int] = None
    session_id: Optional[str] = None


class AIModelResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    provider: str
    usage: Dict[str, int]
    choices: List[Dict[str, Any]]
    cost_usd: float
    response_time_ms: int


class StreamingResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]


# Usage Analytics Schemas
class UsageAnalytics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_cost_usd: float
    average_response_time: float
    top_models: List[Dict[str, Any]]
    usage_by_hour: Dict[str, int]


class UserUsageStats(BaseModel):
    user_id: int
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    credits_used: float
    favorite_models: List[str]
    last_request: Optional[datetime]


# Model Health Schemas
class ModelHealthStatus(BaseModel):
    provider: APIKeyProvider
    model_name: str
    status: str
    response_time_avg: float
    success_rate: float
    error_count: int
    last_error: Optional[str]
    last_check: datetime


class SystemHealthStatus(BaseModel):
    overall_status: str
    total_models: int
    healthy_models: int
    degraded_models: int
    down_models: int
    model_health: List[ModelHealthStatus]


# Load Balancer Schemas
class LoadBalancerConfig(BaseModel):
    model_name: str
    provider_weights: Dict[str, float]
    fallback_order: List[str]
    enabled: bool = True
    min_healthy_keys: int = 1
    health_check_interval: int = 300


class LoadBalancerStatus(BaseModel):
    model_name: str
    current_provider: str
    healthy_providers: List[str]
    total_requests: int
    success_rate: float
    average_response_time: float


# API Key Management Schemas
class APIKeyHealthCheck(BaseModel):
    api_key_id: int
    provider: APIKeyProvider
    status: APIKeyStatus
    response_time_ms: Optional[int]
    error_message: Optional[str]
    checked_at: datetime


class BulkAPIKeyUpdate(BaseModel):
    api_key_ids: List[int]
    status: Optional[APIKeyStatus] = None
    monthly_limit: Optional[float] = None


# Community Features Schemas
class ContributorLeaderboard(BaseModel):
    rank: int
    user_id: int
    username: str
    total_donated_usd: float
    contribution_tier: ContributionTier
    credits_earned: float
    models_enabled: int


class CommunityStats(BaseModel):
    total_contributors: int
    total_api_keys: int
    total_donated_value: float
    models_available: List[str]
    monthly_requests: int
    community_savings: float  # vs individual API costs


# Advanced Features Schemas
class ModelComparison(BaseModel):
    model_a: str
    model_b: str
    prompt: str
    response_a: str
    response_b: str
    cost_comparison: Dict[str, float]
    performance_metrics: Dict[str, float]


class ModelRecommendation(BaseModel):
    recommended_model: str
    confidence: float
    reasons: List[str]
    estimated_cost: float
    expected_quality: float


class AIModelBenchmark(BaseModel):
    model_name: str
    provider: str
    benchmark_type: str
    score: float
    test_date: datetime
    sample_size: int
    metrics: Dict[str, float]


# WebSocket Schemas for Real-time Updates
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class APIKeyStatusUpdate(BaseModel):
    api_key_id: int
    old_status: APIKeyStatus
    new_status: APIKeyStatus
    reason: Optional[str]


class UsageAlert(BaseModel):
    user_id: int
    alert_type: str  # quota_warning, quota_exceeded, credits_low
    message: str
    current_usage: float
    limit: float