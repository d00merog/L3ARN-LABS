"""
WebVM Integration Schemas
Pydantic models for browser-based virtual machine operations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class VMEnvironmentType(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    JAVA = "java"
    RUST = "rust"
    GO = "go"
    LINUX_FULL = "linux_full"
    CUSTOM = "custom"


class VMStatus(str, Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


# WebVM Instance Schemas
class WebVMInstanceCreate(BaseModel):
    environment_type: VMEnvironmentType
    instance_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    cpu_cores: int = Field(default=1, ge=1, le=4)
    memory_mb: int = Field(default=256, ge=128, le=2048)
    disk_mb: int = Field(default=512, ge=256, le=4096)
    network_enabled: bool = Field(default=False)
    is_persistent: bool = Field(default=False)
    environment_variables: Optional[Dict[str, str]] = None
    course_id: Optional[int] = None
    assignment_id: Optional[int] = None
    lesson_id: Optional[int] = None


class WebVMInstanceInfo(BaseModel):
    id: int
    session_id: str
    environment_type: VMEnvironmentType
    status: VMStatus
    instance_name: str
    description: Optional[str]
    cpu_cores: int
    memory_mb: int
    disk_mb: int
    network_enabled: bool
    startup_time_ms: Optional[int]
    last_activity: datetime
    total_runtime_seconds: int
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_usage_mb: float
    is_persistent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebVMInstanceUpdate(BaseModel):
    instance_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[VMStatus] = None
    environment_variables: Optional[Dict[str, str]] = None


# Code Execution Schemas
class CodeExecutionRequest(BaseModel):
    language: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1)
    input_data: Optional[str] = None
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    memory_limit_mb: int = Field(default=256, ge=64, le=1024)
    is_assignment: bool = Field(default=False)
    assignment_id: Optional[int] = None


class CodeExecutionResult(BaseModel):
    id: int
    language: str
    output: Optional[str]
    error_output: Optional[str]
    exit_code: Optional[int]
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[float]
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    test_results: Optional[Dict[str, Any]]
    grade_score: Optional[float]
    ai_feedback: Optional[str]
    code_quality_score: Optional[float]
    suggestions: Optional[List[str]]
    
    class Config:
        from_attributes = True


class CodeExecutionDetailed(CodeExecutionResult):
    code: str
    input_data: Optional[str]
    vm_instance_id: int


# File Management Schemas
class WebVMFileCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    filepath: str = Field(..., min_length=1, max_length=500)
    file_type: str = Field(..., regex="^(source|data|config|binary)$")
    content: Optional[str] = None
    is_executable: bool = Field(default=False)
    is_readonly: bool = Field(default=False)
    permissions: str = Field(default="644", regex="^[0-7]{3}$")
    assignment_id: Optional[int] = None


class WebVMFileInfo(BaseModel):
    id: int
    filename: str
    filepath: str
    file_type: str
    content_hash: Optional[str]
    size_bytes: int
    is_executable: bool
    is_readonly: bool
    permissions: str
    version: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    is_template: bool
    is_solution: bool
    
    class Config:
        from_attributes = True


class WebVMFileUpdate(BaseModel):
    content: Optional[str] = None
    is_executable: Optional[bool] = None
    is_readonly: Optional[bool] = None
    permissions: Optional[str] = Field(None, regex="^[0-7]{3}$")


class WebVMFileContent(BaseModel):
    id: int
    filename: str
    filepath: str
    content: Optional[str]
    file_type: str
    size_bytes: int
    modified_at: datetime


# Template Schemas
class WebVMTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    environment_type: VMEnvironmentType
    base_image: str = Field(..., min_length=1, max_length=100)
    pre_installed_packages: List[str] = Field(default=[])
    default_files: Dict[str, str] = Field(default={})
    startup_script: Optional[str] = None
    max_cpu_cores: int = Field(default=2, ge=1, le=4)
    max_memory_mb: int = Field(default=512, ge=128, le=2048)
    max_disk_mb: int = Field(default=1024, ge=256, le=4096)
    max_runtime_minutes: int = Field(default=60, ge=5, le=240)
    difficulty_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced)$")
    subject_area: Optional[str] = Field(None, max_length=50)
    learning_objectives: List[str] = Field(default=[])


class WebVMTemplateInfo(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment_type: VMEnvironmentType
    base_image: str
    pre_installed_packages: List[str]
    max_cpu_cores: int
    max_memory_mb: int
    max_disk_mb: int
    max_runtime_minutes: int
    difficulty_level: Optional[str]
    subject_area: Optional[str]
    learning_objectives: List[str]
    usage_count: int
    success_rate: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebVMTemplateDetailed(WebVMTemplateInfo):
    default_files: Dict[str, str]
    startup_script: Optional[str]


# Session Management Schemas
class WebVMSessionCreate(BaseModel):
    max_concurrent_vms: int = Field(default=3, ge=1, le=10)
    resource_quota_mb: int = Field(default=1024, ge=512, le=8192)
    session_duration_hours: int = Field(default=24, ge=1, le=168)


class WebVMSessionInfo(BaseModel):
    id: int
    session_token: str
    webgpu_supported: bool
    webassembly_supported: bool
    browser_performance_score: Optional[float]
    active_vm_instances: List[str]
    max_concurrent_vms: int
    resource_quota_mb: int
    resource_used_mb: int
    last_activity: datetime
    total_session_time: int
    commands_executed: int
    files_created: int
    started_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


# Resource Monitoring Schemas
class ResourceUsageSnapshot(BaseModel):
    vm_instance_id: int
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_usage_mb: float
    network_bytes_in: int = 0
    network_bytes_out: int = 0
    response_time_ms: Optional[int] = None
    gpu_usage_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    recorded_at: datetime


class ResourceUsageHistory(BaseModel):
    vm_instance_id: int
    time_range_hours: int
    samples: List[ResourceUsageSnapshot]
    average_cpu: float
    average_memory: float
    peak_cpu: float
    peak_memory: float


# Collaboration Schemas
class WebVMCollaborationCreate(BaseModel):
    is_public: bool = Field(default=False)
    max_collaborators: int = Field(default=5, ge=1, le=20)
    allow_code_editing: bool = Field(default=True)
    allow_file_management: bool = Field(default=False)
    allow_execution: bool = Field(default=True)
    invited_users: List[int] = Field(default=[])
    access_password: Optional[str] = Field(None, min_length=4, max_length=50)
    duration_hours: int = Field(default=24, ge=1, le=168)


class WebVMCollaborationInfo(BaseModel):
    id: int
    vm_instance_id: int
    owner_user_id: int
    is_public: bool
    max_collaborators: int
    allow_code_editing: bool
    allow_file_management: bool
    allow_execution: bool
    active_collaborators: List[int]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CollaborationAction(BaseModel):
    action_type: str = Field(..., regex="^(join|leave|execute|edit|save)$")
    data: Dict[str, Any] = Field(default={})
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Educational Integration Schemas
class EducationalIntegrationCreate(BaseModel):
    content_type: str = Field(..., regex="^(assignment|quiz|lab|project)$")
    content_id: int
    course_id: Optional[int] = None
    auto_grading_enabled: bool = Field(default=False)
    test_cases: Optional[List[Dict[str, Any]]] = None
    expected_outputs: Optional[List[str]] = None
    grading_criteria: Optional[Dict[str, Any]] = None


class EducationalIntegrationInfo(BaseModel):
    id: int
    content_type: str
    content_id: int
    course_id: Optional[int]
    auto_grading_enabled: bool
    completion_status: str
    final_score: Optional[float]
    ai_feedback: Optional[str]
    validation_requested: bool
    consensus_score: Optional[float]
    started_at: datetime
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AssignmentSubmission(BaseModel):
    files_to_submit: List[int] = Field(..., min_items=1)
    submission_notes: Optional[str] = Field(None, max_length=1000)
    request_ai_feedback: bool = Field(default=True)
    request_bittensor_validation: bool = Field(default=False)


# WebGPU and Performance Schemas
class WebGPUCapabilities(BaseModel):
    supported: bool
    adapter_info: Optional[Dict[str, Any]] = None
    features: List[str] = Field(default=[])
    limits: Dict[str, Any] = Field(default={})
    browser_vendor: Optional[str] = None
    browser_version: Optional[str] = None


class PerformanceBenchmark(BaseModel):
    vm_instance_id: int
    benchmark_type: str = Field(..., regex="^(cpu|memory|disk|gpu|network)$")
    score: float
    details: Dict[str, Any] = Field(default={})
    browser_info: Dict[str, str] = Field(default={})
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Analytics and Reporting Schemas
class WebVMUsageAnalytics(BaseModel):
    user_id: int
    time_period_days: int
    total_vm_instances: int
    total_execution_time_hours: float
    total_code_executions: int
    favorite_languages: List[str]
    average_session_duration_minutes: float
    success_rate: float
    resource_efficiency_score: float
    collaboration_sessions: int


class SystemWebVMStats(BaseModel):
    total_active_instances: int
    total_users_active: int
    resource_utilization_percent: float
    average_startup_time_ms: float
    success_rate: float
    popular_environments: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]


# Error and Status Schemas
class WebVMError(BaseModel):
    error_type: str
    error_message: str
    error_code: Optional[str]
    vm_instance_id: Optional[int]
    execution_id: Optional[int]
    timestamp: datetime
    context: Optional[Dict[str, Any]]


class WebVMHealthCheck(BaseModel):
    vm_instance_id: int
    status: VMStatus
    cpu_responsive: bool
    memory_available: bool
    disk_accessible: bool
    network_connectivity: bool
    webgpu_functional: bool
    overall_health: str  # healthy, degraded, unhealthy
    last_checked: datetime


# Real-time Communication Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class VMStatusUpdate(BaseModel):
    vm_instance_id: int
    old_status: VMStatus
    new_status: VMStatus
    reason: Optional[str]
    timestamp: datetime


class CollaborationUpdate(BaseModel):
    collaboration_id: int
    action: CollaborationAction
    user_id: int
    affected_files: List[str] = Field(default=[])


# Configuration Schemas
class WebVMConfig(BaseModel):
    max_instances_per_user: int = Field(default=5, ge=1, le=20)
    max_session_duration_hours: int = Field(default=24, ge=1, le=168)
    default_resource_quota_mb: int = Field(default=1024, ge=512, le=8192)
    enable_gpu_acceleration: bool = Field(default=True)
    enable_networking: bool = Field(default=False)
    enable_collaboration: bool = Field(default=True)
    auto_save_interval_minutes: int = Field(default=5, ge=1, le=60)
    execution_timeout_seconds: int = Field(default=30, ge=5, le=300)
    file_size_limit_mb: int = Field(default=10, ge=1, le=100)