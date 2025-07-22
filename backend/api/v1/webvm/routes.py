"""
WebVM Routes
FastAPI routes for browser-based virtual machine operations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from .service import WebVMService
from .models import WebVMInstance, CodeExecution, WebVMFile, WebVMTemplate, VMStatus
from .schemas import (
    WebVMInstanceCreate, WebVMInstanceInfo, WebVMInstanceUpdate,
    CodeExecutionRequest, CodeExecutionResult, CodeExecutionDetailed,
    WebVMFileCreate, WebVMFileInfo, WebVMFileContent,
    WebVMTemplateCreate, WebVMTemplateInfo,
    WebVMCollaborationCreate, WebVMCollaborationInfo, CollaborationAction,
    EducationalIntegrationCreate, EducationalIntegrationInfo,
    AssignmentSubmission, WebVMUsageAnalytics, SystemWebVMStats,
    ResourceUsageSnapshot, WebVMHealthCheck, WebVMConfig
)
from ....core.database import get_db
from ....core.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/webvm", tags=["WebVM"])
webvm_service = WebVMService()

# VM Instance Management
@router.post("/instances", response_model=WebVMInstanceInfo)
async def create_vm_instance(
    vm_data: WebVMInstanceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new WebVM instance"""
    
    try:
        vm_instance = await webvm_service.create_vm_instance(
            db, current_user["id"], vm_data
        )
        
        # Start resource monitoring
        background_tasks.add_task(
            webvm_service.monitor_resource_usage,
            db, vm_instance
        )
        
        return WebVMInstanceInfo.from_orm(vm_instance)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create VM instance: {str(e)}")


@router.get("/instances", response_model=List[WebVMInstanceInfo])
async def get_user_vm_instances(
    status: Optional[VMStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all VM instances for the current user"""
    
    instances = await webvm_service.get_vm_instances_by_user(
        db, current_user["id"], status
    )
    
    return [WebVMInstanceInfo.from_orm(instance) for instance in instances]


@router.get("/instances/{instance_id}", response_model=WebVMInstanceInfo)
async def get_vm_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific VM instance details"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    return WebVMInstanceInfo.from_orm(instance)


@router.patch("/instances/{instance_id}", response_model=WebVMInstanceInfo)
async def update_vm_instance(
    instance_id: int,
    update_data: WebVMInstanceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update VM instance configuration"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(instance, field, value)
    
    db.commit()
    db.refresh(instance)
    
    return WebVMInstanceInfo.from_orm(instance)


@router.delete("/instances/{instance_id}")
async def terminate_vm_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Terminate and delete VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    await webvm_service.terminate_vm_instance(db, instance)
    
    return {"message": "VM instance terminated successfully"}


# Code Execution
@router.post("/instances/{instance_id}/execute", response_model=CodeExecutionResult)
async def execute_code(
    instance_id: int,
    execution_request: CodeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Execute code in WebVM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    if instance.status != VMStatus.RUNNING:
        raise HTTPException(status_code=400, detail="VM instance is not running")
    
    try:
        execution = await webvm_service.execute_code(db, instance, execution_request)
        return CodeExecutionResult.from_orm(execution)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")


@router.get("/instances/{instance_id}/executions", response_model=List[CodeExecutionResult])
async def get_execution_history(
    instance_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get code execution history for VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    executions = db.query(CodeExecution).filter(
        CodeExecution.vm_instance_id == instance_id
    ).order_by(CodeExecution.started_at.desc()).limit(limit).all()
    
    return [CodeExecutionResult.from_orm(execution) for execution in executions]


@router.get("/executions/{execution_id}", response_model=CodeExecutionDetailed)
async def get_execution_details(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed execution information"""
    
    execution = db.query(CodeExecution).filter(
        CodeExecution.id == execution_id,
        CodeExecution.user_id == current_user["id"]
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return CodeExecutionDetailed.from_orm(execution)


# File Management
@router.post("/instances/{instance_id}/files", response_model=WebVMFileInfo)
async def create_file(
    instance_id: int,
    file_data: WebVMFileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new file in VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    file_record = WebVMFile(
        vm_instance_id=instance_id,
        user_id=current_user["id"],
        filename=file_data.filename,
        filepath=file_data.filepath,
        file_type=file_data.file_type,
        content=file_data.content,
        is_executable=file_data.is_executable,
        is_readonly=file_data.is_readonly,
        permissions=file_data.permissions,
        assignment_id=file_data.assignment_id
    )
    
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    
    return WebVMFileInfo.from_orm(file_record)


@router.get("/instances/{instance_id}/files", response_model=List[WebVMFileInfo])
async def get_instance_files(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all files for VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    files = db.query(WebVMFile).filter(
        WebVMFile.vm_instance_id == instance_id
    ).all()
    
    return [WebVMFileInfo.from_orm(file) for file in files]


@router.get("/files/{file_id}", response_model=WebVMFileContent)
async def get_file_content(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get file content"""
    
    file_record = db.query(WebVMFile).filter(
        WebVMFile.id == file_id,
        WebVMFile.user_id == current_user["id"]
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return WebVMFileContent.from_orm(file_record)


# Collaboration
@router.post("/instances/{instance_id}/collaborate", response_model=WebVMCollaborationInfo)
async def create_collaboration(
    instance_id: int,
    collaboration_data: WebVMCollaborationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create collaborative session for VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    collaboration = await webvm_service.create_collaboration_session(
        db, instance, collaboration_data
    )
    
    return WebVMCollaborationInfo.from_orm(collaboration)


# Educational Integration
@router.post("/instances/{instance_id}/educational", response_model=EducationalIntegrationInfo)
async def create_educational_integration(
    instance_id: int,
    integration_data: EducationalIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Connect VM instance to educational content"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    integration = await webvm_service.create_educational_integration(
        db, instance, integration_data
    )
    
    return EducationalIntegrationInfo.from_orm(integration)


@router.post("/instances/{instance_id}/submit", response_model=dict)
async def submit_assignment(
    instance_id: int,
    submission: AssignmentSubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit assignment from VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    # Get educational integration
    integration = await webvm_service.get_educational_integration(
        db, instance_id, current_user["id"]
    )
    
    if not integration:
        raise HTTPException(status_code=404, detail="Educational integration not found")
    
    # Update submission status
    integration.completion_status = "completed"
    integration.submitted_at = datetime.utcnow()
    db.commit()
    
    # Process submission in background
    if submission.request_bittensor_validation:
        # Background task for Bittensor validation would be added here
        pass
    
    return {
        "message": "Assignment submitted successfully",
        "submission_id": integration.id,
        "files_submitted": len(submission.files_to_submit)
    }


# Resource Monitoring
@router.get("/instances/{instance_id}/resources", response_model=ResourceUsageSnapshot)
async def get_resource_usage(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current resource usage for VM instance"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    return ResourceUsageSnapshot(
        vm_instance_id=instance.id,
        cpu_usage_percent=instance.cpu_usage_percent,
        memory_usage_mb=instance.memory_usage_mb,
        disk_usage_mb=instance.disk_usage_mb,
        recorded_at=instance.last_activity
    )


@router.get("/instances/{instance_id}/health", response_model=WebVMHealthCheck)
async def check_vm_health(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check VM instance health status"""
    
    instance = db.query(WebVMInstance).filter(
        WebVMInstance.id == instance_id,
        WebVMInstance.user_id == current_user["id"]
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="VM instance not found")
    
    # Simulate health check
    health_status = "healthy" if instance.status == VMStatus.RUNNING else "unhealthy"
    
    return WebVMHealthCheck(
        vm_instance_id=instance.id,
        status=instance.status,
        cpu_responsive=instance.status == VMStatus.RUNNING,
        memory_available=instance.memory_usage_mb < instance.memory_mb * 0.9,
        disk_accessible=instance.disk_usage_mb < instance.disk_mb * 0.9,
        network_connectivity=instance.network_enabled,
        webgpu_functional=True,  # Would check actual WebGPU status
        overall_health=health_status,
        last_checked=datetime.utcnow()
    )


# Analytics and Statistics
@router.get("/analytics/user", response_model=WebVMUsageAnalytics)
async def get_user_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user WebVM usage analytics"""
    
    # Simulate analytics data
    instances = await webvm_service.get_vm_instances_by_user(db, current_user["id"])
    
    total_executions = db.query(CodeExecution).filter(
        CodeExecution.user_id == current_user["id"]
    ).count()
    
    return WebVMUsageAnalytics(
        user_id=current_user["id"],
        time_period_days=days,
        total_vm_instances=len(instances),
        total_execution_time_hours=sum(i.total_runtime_seconds for i in instances) / 3600,
        total_code_executions=total_executions,
        favorite_languages=["python", "javascript", "cpp"],
        average_session_duration_minutes=45.0,
        success_rate=0.92,
        resource_efficiency_score=0.78,
        collaboration_sessions=3
    )


@router.get("/stats/system", response_model=SystemWebVMStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get system-wide WebVM statistics (admin only)"""
    
    # This would typically require admin permissions
    total_instances = db.query(WebVMInstance).filter(
        WebVMInstance.status.in_([VMStatus.RUNNING, VMStatus.PAUSED])
    ).count()
    
    active_users = db.query(WebVMInstance.user_id).distinct().count()
    
    return SystemWebVMStats(
        total_active_instances=total_instances,
        total_users_active=active_users,
        resource_utilization_percent=65.5,
        average_startup_time_ms=1250.0,
        success_rate=0.94,
        popular_environments=[
            {"environment": "python", "usage_count": 1250},
            {"environment": "javascript", "usage_count": 980},
            {"environment": "cpp", "usage_count": 670}
        ],
        performance_metrics={
            "avg_execution_time_ms": 850.0,
            "avg_memory_usage_mb": 180.5,
            "avg_cpu_usage_percent": 25.3
        }
    )


# WebSocket for real-time collaboration
@router.websocket("/instances/{instance_id}/collaborate/ws")
async def websocket_collaboration(
    websocket: WebSocket,
    instance_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time collaboration"""
    
    await websocket.accept()
    
    try:
        while True:
            # Receive collaboration action
            data = await websocket.receive_text()
            action_data = json.loads(data)
            
            # Process collaboration action
            action = CollaborationAction(**action_data)
            
            # Broadcast to other collaborators (simplified)
            response = {
                "type": "collaboration_update",
                "action": action.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        pass  # Handle disconnection
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))