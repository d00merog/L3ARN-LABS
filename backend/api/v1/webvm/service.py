"""
WebVM Service
Core service for browser-based virtual machine management
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .models import (
    WebVMInstance, CodeExecution, WebVMFile, WebVMTemplate, WebVMSession,
    WebVMResourceUsage, WebVMCollaboration, WebVMEducationalIntegration,
    VMStatus, VMEnvironmentType, ExecutionStatus
)
from .schemas import (
    WebVMInstanceCreate, CodeExecutionRequest, WebVMFileCreate,
    WebVMTemplateCreate, WebVMCollaborationCreate, EducationalIntegrationCreate
)
from ....core.database import get_db


class WebVMService:
    """Core WebVM management service with CheerpX integration"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.vm_instances: Dict[str, Dict] = {}
        self.execution_queue = asyncio.Queue()
        
    async def create_vm_instance(
        self, 
        db: Session, 
        user_id: int, 
        vm_data: WebVMInstanceCreate
    ) -> WebVMInstance:
        """Create new WebVM instance with CheerpX integration"""
        
        # Generate unique session ID
        session_id = f"webvm_{uuid.uuid4().hex[:16]}"
        
        # Create VM instance record
        vm_instance = WebVMInstance(
            user_id=user_id,
            session_id=session_id,
            environment_type=vm_data.environment_type,
            instance_name=vm_data.instance_name,
            description=vm_data.description,
            cpu_cores=vm_data.cpu_cores,
            memory_mb=vm_data.memory_mb,
            disk_mb=vm_data.disk_mb,
            network_enabled=vm_data.network_enabled,
            is_persistent=vm_data.is_persistent,
            environment_variables=vm_data.environment_variables or {},
            course_id=vm_data.course_id,
            assignment_id=vm_data.assignment_id,
            lesson_id=vm_data.lesson_id,
            status=VMStatus.INITIALIZING
        )
        
        db.add(vm_instance)
        db.commit()
        db.refresh(vm_instance)
        
        # Initialize WebAssembly environment
        await self._initialize_webassembly_vm(vm_instance)
        
        return vm_instance
    
    async def _initialize_webassembly_vm(self, vm_instance: WebVMInstance):
        """Initialize WebAssembly VM using CheerpX"""
        
        startup_start = datetime.utcnow()
        
        try:
            # Configure CheerpX environment based on type
            vm_config = await self._get_environment_config(vm_instance.environment_type)
            
            # Initialize WebAssembly runtime
            runtime_info = {
                "session_id": vm_instance.session_id,
                "environment": vm_instance.environment_type.value,
                "memory_mb": vm_instance.memory_mb,
                "disk_mb": vm_instance.disk_mb,
                "network_enabled": vm_instance.network_enabled,
                "startup_time": startup_start.isoformat(),
                "config": vm_config
            }
            
            # Store in active sessions
            self.vm_instances[vm_instance.session_id] = {
                "instance": vm_instance,
                "runtime": runtime_info,
                "status": VMStatus.RUNNING,
                "last_activity": datetime.utcnow()
            }
            
            # Calculate startup time
            startup_time_ms = int((datetime.utcnow() - startup_start).total_seconds() * 1000)
            
            # Update instance with startup metrics
            db = next(get_db())
            vm_instance.startup_time_ms = startup_time_ms
            vm_instance.status = VMStatus.RUNNING
            vm_instance.last_activity = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            # Handle startup failure
            db = next(get_db())
            vm_instance.status = VMStatus.ERROR
            db.commit()
            raise e
    
    async def _get_environment_config(self, env_type: VMEnvironmentType) -> Dict[str, Any]:
        """Get CheerpX configuration for different environments"""
        
        base_config = {
            "webassembly_features": ["simd", "bulk-memory", "sign-ext"],
            "cheerpx_version": "3.0",
            "networking": False,
            "filesystem": "memfs"
        }
        
        environment_configs = {
            VMEnvironmentType.PYTHON: {
                **base_config,
                "image": "python:3.11-slim",
                "interpreter": "/usr/bin/python3",
                "packages": ["numpy", "pandas", "matplotlib"],
                "startup_script": "python --version"
            },
            VMEnvironmentType.JAVASCRIPT: {
                **base_config,
                "image": "node:18-alpine",
                "interpreter": "/usr/local/bin/node",
                "packages": ["lodash", "axios"],
                "startup_script": "node --version"
            },
            VMEnvironmentType.CPP: {
                **base_config,
                "image": "gcc:11",
                "compiler": "/usr/bin/g++",
                "packages": ["build-essential"],
                "startup_script": "g++ --version"
            },
            VMEnvironmentType.JAVA: {
                **base_config,
                "image": "openjdk:17-alpine",
                "compiler": "/usr/bin/javac",
                "interpreter": "/usr/bin/java",
                "startup_script": "java --version"
            },
            VMEnvironmentType.RUST: {
                **base_config,
                "image": "rust:1.70",
                "compiler": "/usr/local/cargo/bin/rustc",
                "packages": ["cargo"],
                "startup_script": "rustc --version"
            },
            VMEnvironmentType.GO: {
                **base_config,
                "image": "golang:1.20-alpine",
                "compiler": "/usr/local/go/bin/go",
                "startup_script": "go version"
            },
            VMEnvironmentType.LINUX_FULL: {
                **base_config,
                "image": "ubuntu:22.04",
                "shell": "/bin/bash",
                "networking": True,
                "packages": ["curl", "wget", "git", "vim"],
                "startup_script": "uname -a"
            }
        }
        
        return environment_configs.get(env_type, base_config)
    
    async def execute_code(
        self,
        db: Session,
        vm_instance: WebVMInstance,
        execution_request: CodeExecutionRequest
    ) -> CodeExecution:
        """Execute code in WebVM with security sandboxing"""
        
        # Create execution record
        execution = CodeExecution(
            vm_instance_id=vm_instance.id,
            user_id=vm_instance.user_id,
            language=execution_request.language,
            code=execution_request.code,
            input_data=execution_request.input_data,
            is_assignment=execution_request.is_assignment,
            assignment_id=execution_request.assignment_id,
            status=ExecutionStatus.PENDING.value
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Execute in WebAssembly sandbox
        try:
            execution.status = ExecutionStatus.RUNNING.value
            execution.started_at = datetime.utcnow()
            db.commit()
            
            # Run code execution
            result = await self._execute_in_sandbox(
                vm_instance.session_id,
                execution_request,
                execution_request.timeout_seconds
            )
            
            # Update execution with results
            execution.output = result.get("output")
            execution.error_output = result.get("error_output")
            execution.exit_code = result.get("exit_code", 0)
            execution.execution_time_ms = result.get("execution_time_ms")
            execution.memory_used_mb = result.get("memory_used_mb")
            execution.status = ExecutionStatus.COMPLETED.value if result.get("success") else ExecutionStatus.FAILED.value
            execution.completed_at = datetime.utcnow()
            
            # AI-powered code analysis
            if execution.status == ExecutionStatus.COMPLETED.value:
                await self._analyze_code_quality(db, execution)
            
            db.commit()
            
            # Update VM activity
            vm_instance.last_activity = datetime.utcnow()
            db.commit()
            
        except asyncio.TimeoutError:
            execution.status = ExecutionStatus.TIMEOUT.value
            execution.completed_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            execution.status = ExecutionStatus.FAILED.value
            execution.error_output = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
        
        return execution
    
    async def _execute_in_sandbox(
        self,
        session_id: str,
        execution_request: CodeExecutionRequest,
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """Execute code in WebAssembly sandbox with resource limits"""
        
        if session_id not in self.vm_instances:
            raise ValueError(f"VM instance {session_id} not found")
        
        vm_info = self.vm_instances[session_id]
        start_time = datetime.utcnow()
        
        try:
            # Simulate code execution with WebAssembly
            # In real implementation, this would use CheerpX API
            
            execution_result = await asyncio.wait_for(
                self._simulate_code_execution(execution_request),
                timeout=timeout_seconds
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                **execution_result,
                "execution_time_ms": int(execution_time),
                "success": True
            }
            
        except asyncio.TimeoutError:
            return {
                "output": "",
                "error_output": f"Execution timed out after {timeout_seconds}s",
                "exit_code": 124,
                "execution_time_ms": timeout_seconds * 1000,
                "success": False
            }
    
    async def _simulate_code_execution(self, request: CodeExecutionRequest) -> Dict[str, Any]:
        """Simulate code execution (replace with actual CheerpX integration)"""
        
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
        language_outputs = {
            "python": {
                "output": "Hello from Python WebVM!\nCode executed successfully.",
                "error_output": "",
                "exit_code": 0,
                "memory_used_mb": 12.5
            },
            "javascript": {
                "output": "Hello from Node.js WebVM!\nCode executed successfully.",
                "error_output": "",
                "exit_code": 0,
                "memory_used_mb": 8.2
            },
            "cpp": {
                "output": "Hello from C++ WebVM!\nCompilation and execution successful.",
                "error_output": "",
                "exit_code": 0,
                "memory_used_mb": 15.8
            },
            "java": {
                "output": "Hello from Java WebVM!\nCompilation and execution successful.",
                "error_output": "",
                "exit_code": 0,
                "memory_used_mb": 25.4
            }
        }
        
        return language_outputs.get(request.language.lower(), {
            "output": f"Executed {request.language} code successfully",
            "error_output": "",
            "exit_code": 0,
            "memory_used_mb": 10.0
        })
    
    async def _analyze_code_quality(self, db: Session, execution: CodeExecution):
        """AI-powered code quality analysis"""
        
        # Simulate AI analysis
        quality_metrics = {
            "code_quality_score": 0.85,
            "suggestions": [
                "Consider using more descriptive variable names",
                "Add comments for complex logic",
                "Consider error handling for edge cases"
            ],
            "ai_feedback": "Good code structure with room for minor improvements in readability."
        }
        
        execution.code_quality_score = quality_metrics["code_quality_score"]
        execution.suggestions = quality_metrics["suggestions"]
        execution.ai_feedback = quality_metrics["ai_feedback"]
    
    async def create_collaboration_session(
        self,
        db: Session,
        vm_instance: WebVMInstance,
        collaboration_data: WebVMCollaborationCreate
    ) -> WebVMCollaboration:
        """Create collaborative WebVM session"""
        
        collaboration = WebVMCollaboration(
            vm_instance_id=vm_instance.id,
            owner_user_id=vm_instance.user_id,
            is_public=collaboration_data.is_public,
            max_collaborators=collaboration_data.max_collaborators,
            allow_code_editing=collaboration_data.allow_code_editing,
            allow_file_management=collaboration_data.allow_file_management,
            allow_execution=collaboration_data.allow_execution,
            invited_users=collaboration_data.invited_users,
            access_password=collaboration_data.access_password,
            expires_at=datetime.utcnow() + timedelta(hours=collaboration_data.duration_hours)
        )
        
        db.add(collaboration)
        db.commit()
        db.refresh(collaboration)
        
        return collaboration
    
    async def get_vm_instances_by_user(
        self,
        db: Session,
        user_id: int,
        status_filter: Optional[VMStatus] = None
    ) -> List[WebVMInstance]:
        """Get VM instances for a user"""
        
        query = db.query(WebVMInstance).filter(WebVMInstance.user_id == user_id)
        
        if status_filter:
            query = query.filter(WebVMInstance.status == status_filter)
        
        return query.order_by(desc(WebVMInstance.created_at)).all()
    
    async def monitor_resource_usage(self, db: Session, vm_instance: WebVMInstance):
        """Monitor and record resource usage"""
        
        if vm_instance.session_id not in self.vm_instances:
            return
        
        # Simulate resource monitoring
        resource_usage = WebVMResourceUsage(
            vm_instance_id=vm_instance.id,
            user_id=vm_instance.user_id,
            cpu_usage_percent=min(95.0, max(5.0, 15.5 + (hash(vm_instance.session_id) % 20))),
            memory_usage_mb=min(vm_instance.memory_mb * 0.9, max(10.0, vm_instance.memory_mb * 0.3)),
            disk_usage_mb=min(vm_instance.disk_mb * 0.8, max(5.0, vm_instance.disk_mb * 0.2)),
            network_bytes_in=1024 * (hash(vm_instance.session_id) % 100),
            network_bytes_out=512 * (hash(vm_instance.session_id) % 50),
            response_time_ms=50 + (hash(vm_instance.session_id) % 100)
        )
        
        db.add(resource_usage)
        
        # Update VM instance with current usage
        vm_instance.cpu_usage_percent = resource_usage.cpu_usage_percent
        vm_instance.memory_usage_mb = resource_usage.memory_usage_mb
        vm_instance.disk_usage_mb = resource_usage.disk_usage_mb
        
        db.commit()
    
    async def terminate_vm_instance(self, db: Session, vm_instance: WebVMInstance):
        """Safely terminate WebVM instance"""
        
        # Remove from active sessions
        if vm_instance.session_id in self.vm_instances:
            del self.vm_instances[vm_instance.session_id]
        
        # Update database record
        vm_instance.status = VMStatus.TERMINATED
        vm_instance.terminated_at = datetime.utcnow()
        
        # Calculate total runtime
        if vm_instance.created_at:
            runtime_seconds = (datetime.utcnow() - vm_instance.created_at).total_seconds()
            vm_instance.total_runtime_seconds = int(runtime_seconds)
        
        db.commit()
    
    async def get_educational_integration(
        self,
        db: Session,
        vm_instance_id: int,
        user_id: int
    ) -> Optional[WebVMEducationalIntegration]:
        """Get educational integration for VM instance"""
        
        return db.query(WebVMEducationalIntegration).filter(
            and_(
                WebVMEducationalIntegration.vm_instance_id == vm_instance_id,
                WebVMEducationalIntegration.user_id == user_id
            )
        ).first()
    
    async def create_educational_integration(
        self,
        db: Session,
        vm_instance: WebVMInstance,
        integration_data: EducationalIntegrationCreate
    ) -> WebVMEducationalIntegration:
        """Create educational content integration"""
        
        integration = WebVMEducationalIntegration(
            vm_instance_id=vm_instance.id,
            user_id=vm_instance.user_id,
            content_type=integration_data.content_type,
            content_id=integration_data.content_id,
            course_id=integration_data.course_id,
            auto_grading_enabled=integration_data.auto_grading_enabled,
            test_cases=integration_data.test_cases,
            expected_outputs=integration_data.expected_outputs,
            grading_criteria=integration_data.grading_criteria,
            completion_status="in_progress"
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        return integration