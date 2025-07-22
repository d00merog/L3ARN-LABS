"""
Bittensor Integration Models
Decentralized AI network data models for educational content validation
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ...core.database import Base


class SubnetType(str, enum.Enum):
    TEXT_PROMPTING = "text_prompting"  # netuid 1
    COMPUTE = "compute"  # netuid 27
    EDUCATIONAL = "educational"  # custom educational subnet
    IMAGE_GENERATION = "image_generation"
    TRANSLATION = "translation"
    STORAGE = "storage"


class ValidationType(str, enum.Enum):
    CONTENT_QUALITY = "content_quality"
    FACT_CHECKING = "fact_checking"
    EDUCATIONAL_VALUE = "educational_value"
    CODE_CORRECTNESS = "code_correctness"
    ASSIGNMENT_GRADING = "assignment_grading"


class BittensorNode(Base):
    """Bittensor network node configuration and status"""
    __tablename__ = "bittensor_nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String(20), nullable=False)  # validator, miner, client
    hotkey = Column(String(100), unique=True, nullable=False)
    coldkey = Column(String(100), nullable=False)
    netuid = Column(Integer, nullable=False)
    subnet_type = Column(Enum(SubnetType), nullable=False)
    uid = Column(Integer, nullable=True)  # UID in the subnet
    ip_address = Column(String(45), nullable=True)
    port = Column(Integer, default=8091)
    stake = Column(Float, default=0.0)
    trust = Column(Float, default=0.0)
    consensus = Column(Float, default=0.0)
    incentive = Column(Float, default=0.0)
    dividends = Column(Float, default=0.0)
    emission = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    last_update = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    validations = relationship("BittensorValidation", back_populates="node")
    queries = relationship("BittensorQuery", back_populates="node")


class BittensorQuery(Base):
    """Log of queries sent to Bittensor network"""
    __tablename__ = "bittensor_queries"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("bittensor_nodes.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(100), nullable=True)
    query_type = Column(String(50), nullable=False)  # search, validation, generation
    input_data = Column(JSON, nullable=False)
    target_miners = Column(JSON, nullable=True)  # List of target miner UIDs
    responses_received = Column(Integer, default=0)
    consensus_score = Column(Float, nullable=True)
    final_result = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    cost_tao = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    node = relationship("BittensorNode", back_populates="queries")
    responses = relationship("BittensorResponse", back_populates="query")


class BittensorResponse(Base):
    """Individual responses from Bittensor miners"""
    __tablename__ = "bittensor_responses"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("bittensor_queries.id"), nullable=False)
    miner_uid = Column(Integer, nullable=False)
    miner_hotkey = Column(String(100), nullable=False)
    response_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    trust_score = Column(Float, nullable=True)
    incentive_score = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    is_valid = Column(Boolean, default=True)
    weight_assigned = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    query = relationship("BittensorQuery", back_populates="responses")


class BittensorValidation(Base):
    """Educational content validations using Bittensor network"""
    __tablename__ = "bittensor_validations"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("bittensor_nodes.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    content_id = Column(Integer, nullable=True)  # Course, lesson, assignment ID
    content_type = Column(String(50), nullable=False)  # course, lesson, assignment, quiz
    validation_type = Column(Enum(ValidationType), nullable=False)
    content_hash = Column(String(64), nullable=False)  # SHA-256 hash of content
    original_content = Column(Text, nullable=False)
    validation_prompt = Column(Text, nullable=False)
    miner_responses = Column(JSON, nullable=False)  # All miner responses
    consensus_result = Column(JSON, nullable=False)  # Final consensus result
    consensus_score = Column(Float, nullable=False)  # 0.0 to 1.0
    validator_count = Column(Integer, nullable=False)
    agreement_ratio = Column(Float, nullable=False)  # Ratio of miners in agreement
    quality_score = Column(Float, nullable=True)  # Overall quality rating
    fact_accuracy = Column(Float, nullable=True)  # Fact-checking accuracy
    educational_value = Column(Float, nullable=True)  # Educational value score
    is_approved = Column(Boolean, default=False)
    approval_threshold = Column(Float, default=0.7)
    tao_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    node = relationship("BittensorNode", back_populates="validations")


class TAOTransaction(Base):
    """TAO token transactions for educational rewards"""
    __tablename__ = "tao_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # earn, spend, transfer
    amount_tao = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    activity_type = Column(String(50), nullable=True)  # assignment, quiz, content_creation
    activity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    bittensor_block = Column(Integer, nullable=True)
    transaction_hash = Column(String(64), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    confirmation_block = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())


class UserTAOWallet(Base):
    """User TAO token wallet and balance tracking"""
    __tablename__ = "user_tao_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    hotkey = Column(String(100), unique=True, nullable=True)
    coldkey = Column(String(100), unique=True, nullable=True)
    current_balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    pending_transactions = Column(Float, default=0.0)
    last_sync_block = Column(Integer, nullable=True)
    last_sync_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class BittensorSubnet(Base):
    """Bittensor subnet information and configuration"""
    __tablename__ = "bittensor_subnets"

    id = Column(Integer, primary_key=True, index=True)
    netuid = Column(Integer, unique=True, nullable=False)
    subnet_type = Column(Enum(SubnetType), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    repository_url = Column(String(200), nullable=True)
    registration_cost = Column(Float, default=0.0)
    burn_cost = Column(Float, default=0.0)
    max_validators = Column(Integer, default=64)
    max_miners = Column(Integer, default=1024)
    immunity_period = Column(Integer, default=7200)  # blocks
    min_allowed_weights = Column(Integer, default=1)
    max_weights_limit = Column(Float, default=1.0)
    tempo = Column(Integer, default=99)  # blocks between epochs
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class EducationalMining(Base):
    """Educational mining activities and rewards"""
    __tablename__ = "educational_mining"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # assignment, quiz, peer_review, content_creation
    activity_id = Column(Integer, nullable=False)
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    completion_time_seconds = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    validation_score = Column(Float, nullable=True)  # From Bittensor validation
    base_reward_tao = Column(Float, nullable=False)
    multiplier = Column(Float, default=1.0)
    final_reward_tao = Column(Float, nullable=False)
    is_validated = Column(Boolean, default=False)
    validation_id = Column(Integer, ForeignKey("bittensor_validations.id"), nullable=True)
    mined_at = Column(DateTime, default=func.now())
    validated_at = Column(DateTime, nullable=True)


class NetworkHealth(Base):
    """Bittensor network health monitoring"""
    __tablename__ = "bittensor_network_health"

    id = Column(Integer, primary_key=True, index=True)
    netuid = Column(Integer, nullable=False)
    total_miners = Column(Integer, default=0)
    active_miners = Column(Integer, default=0)
    total_validators = Column(Integer, default=0)
    active_validators = Column(Integer, default=0)
    network_difficulty = Column(Float, default=0.0)
    total_stake = Column(Float, default=0.0)
    emission_rate = Column(Float, default=0.0)
    average_trust = Column(Float, default=0.0)
    average_consensus = Column(Float, default=0.0)
    block_time_avg = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    response_time_avg = Column(Float, default=0.0)
    health_score = Column(Float, default=0.0)  # 0.0 to 1.0
    checked_at = Column(DateTime, default=func.now())


# Index optimizations for better query performance
from sqlalchemy import Index

Index('idx_queries_user_created', BittensorQuery.user_id, BittensorQuery.created_at)
Index('idx_responses_query_miner', BittensorResponse.query_id, BittensorResponse.miner_uid)
Index('idx_validations_content_type', BittensorValidation.content_type, BittensorValidation.validation_type)
Index('idx_transactions_user_type', TAOTransaction.user_id, TAOTransaction.transaction_type)
Index('idx_mining_user_activity', EducationalMining.user_id, EducationalMining.activity_type)
Index('idx_health_netuid_time', NetworkHealth.netuid, NetworkHealth.checked_at)