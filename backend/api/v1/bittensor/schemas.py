"""
Bittensor Integration Schemas
Pydantic models for decentralized AI network operations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class SubnetType(str, Enum):
    TEXT_PROMPTING = "text_prompting"
    COMPUTE = "compute"
    EDUCATIONAL = "educational"
    IMAGE_GENERATION = "image_generation"
    TRANSLATION = "translation"
    STORAGE = "storage"


class ValidationType(str, Enum):
    CONTENT_QUALITY = "content_quality"
    FACT_CHECKING = "fact_checking"
    EDUCATIONAL_VALUE = "educational_value"
    CODE_CORRECTNESS = "code_correctness"
    ASSIGNMENT_GRADING = "assignment_grading"


class NodeType(str, Enum):
    VALIDATOR = "validator"
    MINER = "miner"
    CLIENT = "client"


# Bittensor Node Schemas
class BittensorNodeCreate(BaseModel):
    node_type: NodeType
    hotkey: str = Field(..., min_length=48, max_length=48)
    coldkey: str = Field(..., min_length=48, max_length=48)
    netuid: int = Field(..., ge=1, le=1000)
    subnet_type: SubnetType
    ip_address: Optional[str] = None
    port: int = Field(default=8091, ge=1, le=65535)


class BittensorNodeInfo(BaseModel):
    id: int
    node_type: NodeType
    hotkey: str
    netuid: int
    subnet_type: SubnetType
    uid: Optional[int]
    stake: float
    trust: float
    consensus: float
    incentive: float
    is_active: bool
    last_update: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class BittensorNodeUpdate(BaseModel):
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    is_active: Optional[bool] = None


# Query and Response Schemas
class BittensorQueryCreate(BaseModel):
    query_type: str = Field(..., min_length=1, max_length=50)
    input_data: Dict[str, Any]
    target_miners: Optional[List[int]] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None


class BittensorQueryResult(BaseModel):
    id: int
    query_type: str
    consensus_score: Optional[float]
    final_result: Optional[Dict[str, Any]]
    responses_received: int
    processing_time_ms: Optional[int]
    success: bool
    cost_tao: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class MinerResponse(BaseModel):
    miner_uid: int
    miner_hotkey: str
    response_data: Dict[str, Any]
    confidence_score: Optional[float]
    trust_score: Optional[float]
    response_time_ms: Optional[int]
    weight_assigned: Optional[float]


class BittensorQueryDetailed(BittensorQueryResult):
    input_data: Dict[str, Any]
    responses: List[MinerResponse]
    error_message: Optional[str]


# Validation Schemas
class ValidationRequest(BaseModel):
    content_type: str = Field(..., min_length=1, max_length=50)
    validation_type: ValidationType
    content: str = Field(..., min_length=1)
    additional_context: Optional[Dict[str, Any]] = None
    approval_threshold: float = Field(default=0.7, ge=0.1, le=1.0)


class ValidationResult(BaseModel):
    id: int
    content_type: str
    validation_type: ValidationType
    consensus_score: float
    agreement_ratio: float
    quality_score: Optional[float]
    fact_accuracy: Optional[float]
    educational_value: Optional[float]
    is_approved: bool
    validator_count: int
    tao_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class ValidationDetailed(ValidationResult):
    content_hash: str
    original_content: str
    validation_prompt: str
    miner_responses: Dict[str, Any]
    consensus_result: Dict[str, Any]


# TAO Token Schemas
class TAOTransactionCreate(BaseModel):
    transaction_type: str = Field(..., regex="^(earn|spend|transfer)$")
    amount_tao: float = Field(..., gt=0)
    activity_type: Optional[str] = None
    activity_id: Optional[int] = None
    description: Optional[str] = None


class TAOTransaction(BaseModel):
    id: int
    user_id: int
    transaction_type: str
    amount_tao: float
    balance_before: float
    balance_after: float
    activity_type: Optional[str]
    description: Optional[str]
    is_confirmed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TAOWalletInfo(BaseModel):
    user_id: int
    hotkey: Optional[str]
    coldkey: Optional[str]
    current_balance: float
    total_earned: float
    total_spent: float
    pending_transactions: float
    last_sync_time: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class TAOWalletUpdate(BaseModel):
    hotkey: Optional[str] = Field(None, min_length=48, max_length=48)
    coldkey: Optional[str] = Field(None, min_length=48, max_length=48)


# Educational Mining Schemas
class EducationalMiningActivity(BaseModel):
    activity_type: str = Field(..., min_length=1, max_length=50)
    activity_id: int
    difficulty_level: str = Field(..., regex="^(beginner|intermediate|advanced)$")
    completion_time_seconds: Optional[int] = Field(None, ge=1)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class MiningReward(BaseModel):
    id: int
    user_id: int
    activity_type: str
    activity_id: int
    difficulty_level: str
    quality_score: Optional[float]
    validation_score: Optional[float]
    base_reward_tao: float
    multiplier: float
    final_reward_tao: float
    is_validated: bool
    mined_at: datetime
    validated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Search and Knowledge Schemas
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=50)
    educational_focus: bool = Field(default=True)
    fact_check: bool = Field(default=True)
    target_subnets: Optional[List[int]] = None


class SearchResult(BaseModel):
    title: str
    content: str
    url: Optional[str]
    score: float
    educational_quality: float
    fact_checked: bool
    source_trust: float
    miner_uid: Optional[int]
    timestamp: datetime


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    consensus_score: float
    processing_time_ms: int
    cost_tao: float


class FactCheckRequest(BaseModel):
    statement: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = Field(None, max_length=2000)
    confidence_threshold: float = Field(default=0.7, ge=0.1, le=1.0)


class FactCheckResult(BaseModel):
    statement: str
    verified: bool
    confidence: float
    consensus_ratio: float
    status: str  # verified, likely_true, uncertain, disputed
    sources: List[str]
    explanation: Optional[str]
    miner_count: int
    cost_tao: float
    timestamp: datetime


# Subnet Management Schemas
class SubnetInfo(BaseModel):
    netuid: int
    subnet_type: SubnetType
    name: str
    description: Optional[str]
    registration_cost: float
    max_validators: int
    max_miners: int
    tempo: int
    is_active: bool
    
    class Config:
        from_attributes = True


class SubnetStats(BaseModel):
    netuid: int
    total_miners: int
    active_miners: int
    total_validators: int
    active_validators: int
    total_stake: float
    emission_rate: float
    average_trust: float
    success_rate: float
    health_score: float


class NetworkHealth(BaseModel):
    overall_status: str  # healthy, degraded, down
    total_subnets: int
    active_subnets: int
    subnet_health: List[SubnetStats]
    last_updated: datetime


# Educational Content Generation Schemas
class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    level: str = Field(..., regex="^(beginner|intermediate|advanced)$")
    content_type: str = Field(..., regex="^(explanation|examples|exercises|assessment)$")
    target_length: Optional[int] = Field(None, ge=100, le=5000)
    additional_requirements: Optional[List[str]] = None


class GeneratedContent(BaseModel):
    topic: str
    level: str
    content_type: str
    content: str
    examples: List[str]
    quality_score: float
    educational_value: float
    validation_score: Optional[float]
    cost_tao: float
    generation_time_ms: int
    created_at: datetime


# Analytics and Reporting Schemas
class UserBittensorStats(BaseModel):
    user_id: int
    total_queries: int
    total_validations: int
    total_tao_earned: float
    total_tao_spent: float
    average_validation_score: float
    mining_activities: int
    favorite_subnets: List[int]
    success_rate: float
    last_activity: Optional[datetime]


class SystemBittensorStats(BaseModel):
    total_users: int
    total_queries_today: int
    total_validations_today: int
    total_tao_circulating: float
    active_subnets: int
    network_health_score: float
    average_response_time: float
    community_contributions: int


# WebSocket and Real-time Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class ValidationUpdate(BaseModel):
    validation_id: int
    status: str
    progress: float
    current_validators: int
    preliminary_score: Optional[float]


class MiningUpdate(BaseModel):
    activity_id: int
    status: str  # pending, validating, completed, failed
    current_reward: Optional[float]
    validation_progress: Optional[float]


# Configuration Schemas
class BittensorConfig(BaseModel):
    network: str = Field(default="mainnet", regex="^(mainnet|testnet|local)$")
    subtensor_endpoint: Optional[str] = None
    chain_endpoint: Optional[str] = None
    default_netuid: int = Field(default=1, ge=1, le=1000)
    query_timeout: int = Field(default=30, ge=1, le=300)
    validation_threshold: float = Field(default=0.7, ge=0.1, le=1.0)
    max_miners_per_query: int = Field(default=20, ge=1, le=100)
    enable_caching: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=300, ge=60, le=3600)


# Error Schemas
class BittensorError(BaseModel):
    error_type: str
    error_message: str
    error_code: Optional[str]
    subnet_id: Optional[int]
    miner_uid: Optional[int]
    timestamp: datetime
    context: Optional[Dict[str, Any]]