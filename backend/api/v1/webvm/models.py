"""
WebVM Integration Models
Browser-based virtual machine management for educational computing
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ...core.database import Base


class VMEnvironmentType(str, enum.Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    JAVA = "java"
    RUST = "rust"
    GO = "go"
    LINUX_FULL = "linux_full"
    CUSTOM = "custom"


class VMStatus(str, enum.Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class WebVMInstance(Base):
    """WebVM instance management"""
    __tablename__ = "webvm_instances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    environment_type = Column(Enum(VMEnvironmentType), nullable=False)
    status = Column(Enum(VMStatus), default=VMStatus.INITIALIZING)
    instance_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # VM Configuration
    cpu_cores = Column(Integer, default=1)
    memory_mb = Column(Integer, default=256)
    disk_mb = Column(Integer, default=512)
    network_enabled = Column(Boolean, default=False)
    
    # Runtime Information
    startup_time_ms = Column(Integer, nullable=True)
    last_activity = Column(DateTime, default=func.now())
    total_runtime_seconds = Column(Integer, default=0)
    
    # Resource Usage
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    disk_usage_mb = Column(Float, default=0.0)
    
    # Persistence
    is_persistent = Column(Boolean, default=False)
    snapshot_data = Column(JSON, nullable=True)
    environment_variables = Column(JSON, default=dict)
    installed_packages = Column(JSON, default=list)
    
    # Educational Context
    course_id = Column(Integer, nullable=True)
    assignment_id = Column(Integer, nullable=True)
    lesson_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    terminated_at = Column(DateTime, nullable=True)
    
    # Relationships
    executions = relationship("CodeExecution", back_populates="vm_instance")
    files = relationship("WebVMFile", back_populates="vm_instance")


class CodeExecution(Base):
    """Code execution records in WebVM"""
    __tablename__ = "code_executions"

    id = Column(Integer, primary_key=True, index=True)
    vm_instance_id = Column(Integer, ForeignKey("webvm_instances.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Execution Details
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    input_data = Column(Text, nullable=True)
    
    # Results
    output = Column(Text, nullable=True)
    error_output = Column(Text, nullable=True)
    exit_code = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed, timeout
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Educational Context
    is_assignment = Column(Boolean, default=False)
    assignment_id = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)
    grade_score = Column(Float, nullable=True)
    
    # AI Analysis
    ai_feedback = Column(Text, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    suggestions = Column(JSON, nullable=True)
    
    # Relationships
    vm_instance = relationship("WebVMInstance", back_populates="executions")


class WebVMFile(Base):
    """File system management for WebVM instances"""
    __tablename__ = "webvm_files"

    id = Column(Integer, primary_key=True, index=True)
    vm_instance_id = Column(Integer, ForeignKey("webvm_instances.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # File Details
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # source, data, config, binary
    content = Column(Text, nullable=True)  # For text files
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash
    size_bytes = Column(Integer, default=0)
    
    # Permissions
    is_executable = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    permissions = Column(String(10), default="644")
    
    # Versioning
    version = Column(Integer, default=1)
    parent_version_id = Column(Integer, ForeignKey("webvm_files.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    accessed_at = Column(DateTime, default=func.now())
    
    # Educational Context
    is_template = Column(Boolean, default=False)
    is_solution = Column(Boolean, default=False)
    assignment_id = Column(Integer, nullable=True)
    
    # Relationships
    vm_instance = relationship("WebVMInstance", back_populates="files")
    parent_version = relationship("WebVMFile", remote_side=[id])


class WebVMTemplate(Base):
    """Pre-configured WebVM templates"""
    __tablename__ = "webvm_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    environment_type = Column(Enum(VMEnvironmentType), nullable=False)
    
    # Template Configuration
    base_image = Column(String(100), nullable=False)
    pre_installed_packages = Column(JSON, default=list)
    default_files = Column(JSON, default=dict)  # filename -> content mapping
    startup_script = Column(Text, nullable=True)
    
    # Resource Limits
    max_cpu_cores = Column(Integer, default=2)
    max_memory_mb = Column(Integer, default=512)
    max_disk_mb = Column(Integer, default=1024)
    max_runtime_minutes = Column(Integer, default=60)
    
    # Educational Metadata
    difficulty_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    subject_area = Column(String(50), nullable=True)
    learning_objectives = Column(JSON, default=list)
    
    # Usage Stats
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)  # User ID of creator
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WebVMSession(Base):
    """User WebVM session management"""
    __tablename__ = "webvm_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(100), unique=True, nullable=False)
    
    # Session Details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    browser_info = Column(JSON, nullable=True)
    
    # WebGPU/WebAssembly Support
    webgpu_supported = Column(Boolean, default=False)
    webassembly_supported = Column(Boolean, default=True)
    browser_performance_score = Column(Float, nullable=True)
    
    # Session State
    active_vm_instances = Column(JSON, default=list)
    max_concurrent_vms = Column(Integer, default=3)
    resource_quota_mb = Column(Integer, default=1024)
    resource_used_mb = Column(Integer, default=0)
    
    # Activity Tracking
    last_activity = Column(DateTime, default=func.now())
    total_session_time = Column(Integer, default=0)  # seconds
    commands_executed = Column(Integer, default=0)
    files_created = Column(Integer, default=0)
    
    # Session Lifecycle
    started_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class WebVMResourceUsage(Base):
    """Resource usage tracking for WebVM instances"""
    __tablename__ = "webvm_resource_usage"

    id = Column(Integer, primary_key=True, index=True)
    vm_instance_id = Column(Integer, ForeignKey("webvm_instances.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Resource Metrics
    cpu_usage_percent = Column(Float, nullable=False)
    memory_usage_mb = Column(Float, nullable=False)
    disk_usage_mb = Column(Float, nullable=False)
    network_bytes_in = Column(Integer, default=0)
    network_bytes_out = Column(Integer, default=0)
    
    # Performance Metrics
    response_time_ms = Column(Integer, nullable=True)
    throughput_ops_per_sec = Column(Float, nullable=True)
    error_rate = Column(Float, default=0.0)
    
    # WebGPU Metrics (if applicable)
    gpu_usage_percent = Column(Float, nullable=True)
    gpu_memory_mb = Column(Float, nullable=True)
    webgl_calls_per_sec = Column(Integer, nullable=True)
    
    # Sampling
    sample_interval_seconds = Column(Integer, default=60)
    recorded_at = Column(DateTime, default=func.now())


class WebVMCollaboration(Base):
    """Collaborative WebVM session management"""
    __tablename__ = "webvm_collaborations"

    id = Column(Integer, primary_key=True, index=True)
    vm_instance_id = Column(Integer, ForeignKey("webvm_instances.id"), nullable=False)
    owner_user_id = Column(Integer, nullable=False, index=True)
    
    # Collaboration Settings
    is_public = Column(Boolean, default=False)
    max_collaborators = Column(Integer, default=5)
    allow_code_editing = Column(Boolean, default=True)
    allow_file_management = Column(Boolean, default=False)
    allow_execution = Column(Boolean, default=True)
    
    # Access Control
    invited_users = Column(JSON, default=list)  # List of user IDs
    access_password = Column(String(100), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Session State
    active_collaborators = Column(JSON, default=list)
    collaboration_history = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WebVMEducationalIntegration(Base):
    """Integration with educational content and assessments"""
    __tablename__ = "webvm_educational_integration"

    id = Column(Integer, primary_key=True, index=True)
    vm_instance_id = Column(Integer, ForeignKey("webvm_instances.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Educational Context
    content_type = Column(String(50), nullable=False)  # assignment, quiz, lab, project
    content_id = Column(Integer, nullable=False)
    course_id = Column(Integer, nullable=True)
    
    # Assessment Data
    auto_grading_enabled = Column(Boolean, default=False)
    test_cases = Column(JSON, nullable=True)
    expected_outputs = Column(JSON, nullable=True)
    grading_criteria = Column(JSON, nullable=True)
    
    # Results
    completion_status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    final_score = Column(Float, nullable=True)
    detailed_results = Column(JSON, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    
    # Bittensor Integration
    validation_requested = Column(Boolean, default=False)
    bittensor_validation_id = Column(Integer, nullable=True)
    consensus_score = Column(Float, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=func.now())
    submitted_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)


# Index optimizations for better query performance
from sqlalchemy import Index

Index('idx_vm_instances_user_status', WebVMInstance.user_id, WebVMInstance.status)
Index('idx_executions_vm_user', CodeExecution.vm_instance_id, CodeExecution.user_id)
Index('idx_files_vm_path', WebVMFile.vm_instance_id, WebVMFile.filepath)
Index('idx_sessions_user_active', WebVMSession.user_id, WebVMSession.is_active)
Index('idx_resource_usage_vm_time', WebVMResourceUsage.vm_instance_id, WebVMResourceUsage.recorded_at)
Index('idx_collaboration_vm_owner', WebVMCollaboration.vm_instance_id, WebVMCollaboration.owner_user_id)
Index('idx_educational_content_user', WebVMEducationalIntegration.content_id, WebVMEducationalIntegration.user_id)