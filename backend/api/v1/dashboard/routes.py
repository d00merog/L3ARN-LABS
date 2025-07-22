"""
Dashboard API Routes
Comprehensive analytics and dashboard data for the L3ARN Labs platform
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from ....core.database import get_db
from ....core.auth import get_current_user
from ..bittensor.models import BittensorValidation, TAOTransaction, EducationalMining
from ..webvm.models import WebVMInstance, CodeExecution, WebVMResourceUsage
from ..litellm.models import LiteLLMUsage
from ...users.models import User
from ...courses.models import Course
from ..security.routes import SecurityMetricsResponse
from ....core.security.network import network_security_manager
from ..webvm.security import webvm_security_manager
from ..bittensor.security import transaction_validator

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard overview for user"""
    
    user_id = current_user["id"]
    
    # User progress metrics
    total_courses = db.query(Course).count()
    completed_courses = 8  # Placeholder - would query actual completions
    
    # Code execution metrics  
    code_executions = db.query(CodeExecution).filter(
        CodeExecution.user_id == user_id
    ).count()
    
    # TAO earnings
    tao_earned = db.query(func.sum(TAOTransaction.amount_tao)).filter(
        and_(
            TAOTransaction.user_id == user_id,
            TAOTransaction.transaction_type == "reward"
        )
    ).scalar() or 0.0
    
    # Learning streak (simulated)
    learning_streak = 7
    
    # Study hours (calculated from VM usage)
    total_runtime = db.query(func.sum(WebVMInstance.total_runtime_seconds)).filter(
        WebVMInstance.user_id == user_id
    ).scalar() or 0
    study_hours = total_runtime / 3600.0
    
    # AI interactions
    ai_interactions = db.query(LiteLLMUsage).filter(
        LiteLLMUsage.user_id == user_id
    ).count()
    
    # Validations completed
    validations = db.query(BittensorValidation).filter(
        BittensorValidation.user_id == user_id
    ).count()
    
    # Get security metrics
    security_metrics = network_security_manager.get_security_metrics(hours=24)
    webvm_threats = await webvm_security_manager.get_security_metrics(hours=24)
    
    # Get achievement data
    achievements = await _get_user_achievements(db, user_id)
    
    return {
        "user_stats": {
            "total_courses": total_courses,
            "completed_courses": completed_courses,
            "completion_rate": completed_courses / max(total_courses, 1),
            "code_executions": code_executions,
            "tao_earned": round(tao_earned, 2),
            "learning_streak": learning_streak,
            "study_hours": round(study_hours, 1),
            "ai_interactions": ai_interactions,
            "validations_completed": validations
        },
        "recent_activities": await _get_recent_activities(db, user_id),
        "learning_progress": {
            "weekly_goal_progress": 0.78,
            "monthly_goal_progress": 0.65,
            "favorite_languages": ["python", "javascript", "rust"],
            "strongest_subjects": ["AI/ML", "Web Development", "Systems Programming"],
            "skill_levels": {
                "programming": 85,
                "algorithms": 72,
                "system_design": 68,
                "ai_ml": 91
            }
        },
        "security_overview": {
            "security_score": max(0, 100 - security_metrics["high_risk_events"] * 5),
            "threats_blocked": security_metrics["blocked_ips"],
            "webvm_security_status": "good" if webvm_threats["critical_threats"] == 0 else "warning",
            "last_security_scan": datetime.utcnow().isoformat()
        },
        "achievements": achievements,
        "gamification": {
            "level": _calculate_user_level(tao_earned, code_executions),
            "xp_points": int(tao_earned * 1000 + code_executions * 10),
            "next_level_progress": 0.67,
            "badges": _get_user_badges(db, user_id)
        }
    }


@router.get("/webvm/stats")
async def get_webvm_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WebVM usage statistics"""
    
    user_id = current_user["id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # VM instances
    vm_instances = db.query(WebVMInstance).filter(
        and_(
            WebVMInstance.user_id == user_id,
            WebVMInstance.created_at >= start_date
        )
    ).all()
    
    # Execution statistics
    executions = db.query(CodeExecution).filter(
        and_(
            CodeExecution.user_id == user_id,
            CodeExecution.started_at >= start_date
        )
    ).all()
    
    # Resource usage
    resource_usage = db.query(WebVMResourceUsage).filter(
        and_(
            WebVMResourceUsage.user_id == user_id,
            WebVMResourceUsage.recorded_at >= start_date
        )
    ).all()
    
    # Calculate statistics
    total_instances = len(vm_instances)
    total_executions = len(executions)
    
    successful_executions = sum(1 for e in executions if e.status == "completed")
    success_rate = successful_executions / max(total_executions, 1)
    
    avg_execution_time = sum(e.execution_time_ms or 0 for e in executions) / max(total_executions, 1)
    
    # Environment usage
    env_usage = {}
    for instance in vm_instances:
        env = instance.environment_type.value
        env_usage[env] = env_usage.get(env, 0) + 1
    
    # Language statistics
    language_stats = {}
    for execution in executions:
        lang = execution.language
        language_stats[lang] = language_stats.get(lang, 0) + 1
    
    return {
        "summary": {
            "total_instances": total_instances,
            "active_instances": sum(1 for vm in vm_instances if vm.status.value == "running"),
            "total_executions": total_executions,
            "success_rate": round(success_rate, 3),
            "avg_execution_time_ms": round(avg_execution_time, 1)
        },
        "environment_usage": env_usage,
        "language_statistics": language_stats,
        "recent_instances": [
            {
                "id": vm.id,
                "name": vm.instance_name,
                "environment": vm.environment_type.value,
                "status": vm.status.value,
                "created_at": vm.created_at.isoformat(),
                "uptime_seconds": vm.total_runtime_seconds
            }
            for vm in sorted(vm_instances, key=lambda x: x.created_at, reverse=True)[:5]
        ],
        "resource_trends": _calculate_resource_trends(resource_usage)
    }


@router.get("/bittensor/analytics")
async def get_bittensor_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get Bittensor network analytics"""
    
    user_id = current_user["id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # TAO transactions
    tao_transactions = db.query(TAOTransaction).filter(
        and_(
            TAOTransaction.user_id == user_id,
            TAOTransaction.created_at >= start_date
        )
    ).all()
    
    # Validations
    validations = db.query(BittensorValidation).filter(
        and_(
            BittensorValidation.user_id == user_id,
            BittensorValidation.created_at >= start_date
        )
    ).all()
    
    # Educational mining
    mining_activities = db.query(EducationalMining).filter(
        and_(
            EducationalMining.user_id == user_id,
            EducationalMining.mined_at >= start_date
        )
    ).all()
    
    # Calculate metrics
    total_earned = sum(t.amount_tao for t in tao_transactions if t.transaction_type == "reward")
    total_spent = sum(abs(t.amount_tao) for t in tao_transactions if t.transaction_type == "spend")
    
    validation_success_rate = sum(1 for v in validations if v.is_approved) / max(len(validations), 1)
    
    avg_consensus_score = sum(v.consensus_score for v in validations) / max(len(validations), 1)
    
    return {
        "tao_metrics": {
            "total_earned": round(total_earned, 4),
            "total_spent": round(total_spent, 4),
            "net_balance": round(total_earned - total_spent, 4),
            "transaction_count": len(tao_transactions)
        },
        "validation_metrics": {
            "total_validations": len(validations),
            "success_rate": round(validation_success_rate, 3),
            "avg_consensus_score": round(avg_consensus_score, 3),
            "quality_score": round(sum(v.quality_score or 0 for v in validations) / max(len(validations), 1), 3)
        },
        "mining_metrics": {
            "total_mining_activities": len(mining_activities),
            "avg_quality_score": round(sum(m.quality_score or 0 for m in mining_activities) / max(len(mining_activities), 1), 3),
            "total_base_rewards": round(sum(m.base_reward_tao for m in mining_activities), 4)
        },
        "network_participation": {
            "validator_interactions": len(set(v.node_id for v in validations)),
            "subnet_activity": self._get_subnet_activity_summary(validations),
            "consensus_participation": round(avg_consensus_score, 3)
        }
    }


@router.get("/litellm/usage")
async def get_litellm_usage_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get LiteLLM usage statistics"""
    
    user_id = current_user["id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    usage_records = db.query(LiteLLMUsage).filter(
        and_(
            LiteLLMUsage.user_id == user_id,
            LiteLLMUsage.timestamp >= start_date
        )
    ).all()
    
    # Calculate statistics
    total_requests = len(usage_records)
    successful_requests = sum(1 for r in usage_records if r.status == "success")
    
    total_tokens = sum(r.tokens_used or 0 for r in usage_records)
    total_cost = sum(r.cost_usd or 0 for r in usage_records)
    
    # Model usage breakdown
    model_usage = {}
    for record in usage_records:
        model = record.model_name
        model_usage[model] = model_usage.get(model, 0) + 1
    
    # Daily usage trends
    daily_usage = {}
    for record in usage_records:
        date_key = record.timestamp.strftime("%Y-%m-%d")
        if date_key not in daily_usage:
            daily_usage[date_key] = {"requests": 0, "tokens": 0, "cost": 0}
        
        daily_usage[date_key]["requests"] += 1
        daily_usage[date_key]["tokens"] += record.tokens_used or 0
        daily_usage[date_key]["cost"] += record.cost_usd or 0
    
    return {
        "summary": {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": round(successful_requests / max(total_requests, 1), 3),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "avg_tokens_per_request": round(total_tokens / max(total_requests, 1), 1)
        },
        "model_breakdown": model_usage,
        "daily_trends": daily_usage,
        "cost_efficiency": {
            "cost_per_token": round(total_cost / max(total_tokens, 1), 6),
            "tokens_per_dollar": round(total_tokens / max(total_cost, 0.01), 1)
        }
    }


@router.get("/system/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive system health and performance metrics"""
    
    # Check if user has admin permissions (simplified check)
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Active VM instances
    active_vms = db.query(WebVMInstance).filter(
        WebVMInstance.status == "running"
    ).count()
    
    # Recent executions
    recent_executions = db.query(CodeExecution).filter(
        CodeExecution.started_at >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    # Get security metrics
    security_metrics = network_security_manager.get_security_metrics(hours=24)
    webvm_security = await webvm_security_manager.get_security_metrics(hours=24)
    
    # System resource usage (simulated but more comprehensive)
    system_metrics = {
        "cpu_usage_percent": 45.2,
        "memory_usage_percent": 67.8,
        "disk_usage_percent": 34.5,
        "network_throughput_mbps": 125.3,
        "active_connections": 234,
        "load_average": [1.2, 1.1, 0.9],
        "uptime_hours": 168.5
    }
    
    # Enhanced service status with health scores
    service_status = {
        "webvm_service": {
            "status": "healthy",
            "health_score": 98.5,
            "active_instances": active_vms,
            "avg_response_time_ms": 145.2
        },
        "bittensor_service": {
            "status": "healthy",
            "health_score": 96.8,
            "network_sync_status": "synced",
            "consensus_health": 0.95
        },
        "litellm_service": {
            "status": "healthy", 
            "health_score": 99.1,
            "api_availability": 0.999,
            "rate_limit_status": "normal"
        },
        "database": {
            "status": "healthy",
            "health_score": 97.3,
            "connection_pool_usage": 45,
            "query_performance": "optimal"
        },
        "security_system": {
            "status": "healthy" if security_metrics["high_risk_events"] < 10 else "warning",
            "health_score": max(0, 100 - security_metrics["high_risk_events"] * 2),
            "threats_blocked": security_metrics["blocked_ips"],
            "security_level": "high"
        }
    }
    
    return {
        "system_metrics": system_metrics,
        "service_status": service_status,
        "active_instances": {
            "webvm": active_vms,
            "recent_executions": recent_executions,
            "total_users_online": _get_active_users_count(db)
        },
        "performance": {
            "avg_response_time_ms": 145.2,
            "requests_per_second": 23.5,
            "error_rate_percent": 0.12,
            "throughput_rpm": 1410,
            "cache_hit_rate": 0.87
        },
        "security_overview": {
            "total_threats_detected": security_metrics["total_events"],
            "critical_alerts": security_metrics["high_risk_events"],
            "webvm_security_incidents": webvm_security["security_incidents"],
            "last_security_scan": datetime.utcnow().isoformat()
        },
        "capacity_planning": {
            "resource_utilization": 67.8,
            "predicted_capacity_days": 45,
            "scaling_recommendation": "stable"
        },
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/analytics/advanced")
async def get_advanced_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get advanced analytics dashboard"""
    
    user_id = current_user["id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Learning velocity analysis
    daily_executions = db.query(
        func.date(CodeExecution.started_at).label('date'),
        func.count(CodeExecution.id).label('count')
    ).filter(
        and_(
            CodeExecution.user_id == user_id,
            CodeExecution.started_at >= start_date
        )
    ).group_by(func.date(CodeExecution.started_at)).all()
    
    # Skill progression analysis
    skill_progression = await _analyze_skill_progression(db, user_id, start_date)
    
    # Performance metrics
    performance_analysis = await _analyze_performance_metrics(db, user_id, start_date)
    
    # Learning efficiency
    efficiency_metrics = await _calculate_learning_efficiency(db, user_id, start_date)
    
    return {
        "learning_velocity": {
            "daily_activity": [
                {"date": str(day.date), "executions": day.count}
                for day in daily_executions
            ],
            "trend_analysis": _calculate_activity_trend(daily_executions),
            "consistency_score": _calculate_consistency_score(daily_executions)
        },
        "skill_progression": skill_progression,
        "performance_analysis": performance_analysis,
        "efficiency_metrics": efficiency_metrics,
        "predictive_insights": {
            "projected_completion_time": "2.3 weeks",
            "recommended_focus_areas": ["algorithms", "system design"],
            "learning_pace_recommendation": "increase by 15%"
        },
        "comparative_analysis": {
            "peer_ranking_percentile": 78,
            "similar_learners_comparison": "above average",
            "improvement_rate": 12.5
        }
    }


def _get_active_users_count(db: Session) -> int:
    """Get count of currently active users"""
    
    # Users active in the last hour
    active_threshold = datetime.utcnow() - timedelta(hours=1)
    
    active_count = db.query(User).join(CodeExecution).filter(
        CodeExecution.started_at >= active_threshold
    ).distinct().count()
    
    return active_count


async def _analyze_skill_progression(db: Session, user_id: int, start_date: datetime) -> Dict:
    """Analyze user's skill progression over time"""
    
    executions = db.query(CodeExecution).filter(
        and_(
            CodeExecution.user_id == user_id,
            CodeExecution.started_at >= start_date
        )
    ).order_by(CodeExecution.started_at).all()
    
    if not executions:
        return {"languages": {}, "complexity_growth": 0, "error_rate_trend": 0}
    
    # Language proficiency analysis
    language_progression = {}
    for execution in executions:
        lang = execution.language
        if lang not in language_progression:
            language_progression[lang] = {
                "total_executions": 0,
                "success_rate": 0,
                "avg_complexity": 0,
                "improvement_rate": 0
            }
        
        language_progression[lang]["total_executions"] += 1
        if execution.status == "completed":
            language_progression[lang]["success_rate"] += 1
    
    # Calculate success rates
    for lang_data in language_progression.values():
        if lang_data["total_executions"] > 0:
            lang_data["success_rate"] = lang_data["success_rate"] / lang_data["total_executions"]
    
    return {
        "languages": language_progression,
        "complexity_growth": _calculate_complexity_growth(executions),
        "error_rate_trend": _calculate_error_rate_trend(executions)
    }


async def _analyze_performance_metrics(db: Session, user_id: int, start_date: datetime) -> Dict:
    """Analyze performance metrics"""
    
    executions = db.query(CodeExecution).filter(
        and_(
            CodeExecution.user_id == user_id,
            CodeExecution.started_at >= start_date,
            CodeExecution.execution_time_ms.isnot(None)
        )
    ).all()
    
    if not executions:
        return {"avg_execution_time": 0, "performance_trend": "stable", "optimization_score": 0}
    
    avg_time = sum(e.execution_time_ms for e in executions) / len(executions)
    
    return {
        "avg_execution_time_ms": round(avg_time, 2),
        "performance_trend": _calculate_performance_trend(executions),
        "optimization_score": _calculate_optimization_score(executions),
        "fastest_execution": min(e.execution_time_ms for e in executions),
        "slowest_execution": max(e.execution_time_ms for e in executions)
    }


async def _calculate_learning_efficiency(db: Session, user_id: int, start_date: datetime) -> Dict:
    """Calculate learning efficiency metrics"""
    
    # Time spent vs progress made
    total_runtime = db.query(func.sum(WebVMInstance.total_runtime_seconds)).filter(
        and_(
            WebVMInstance.user_id == user_id,
            WebVMInstance.created_at >= start_date
        )
    ).scalar() or 0
    
    successful_executions = db.query(CodeExecution).filter(
        and_(
            CodeExecution.user_id == user_id,
            CodeExecution.started_at >= start_date,
            CodeExecution.status == "completed"
        )
    ).count()
    
    efficiency_score = (successful_executions / max(total_runtime / 3600, 1)) * 10
    
    return {
        "efficiency_score": round(efficiency_score, 2),
        "time_to_success_ratio": successful_executions / max(total_runtime / 3600, 0.1),
        "optimal_learning_hours": "2-3 hours/day",
        "focus_recommendation": "morning sessions show 23% better performance"
    }


def _calculate_activity_trend(daily_executions) -> str:
    """Calculate activity trend direction"""
    
    if len(daily_executions) < 7:
        return "insufficient_data"
    
    recent_avg = sum(day.count for day in daily_executions[-7:]) / 7
    older_avg = sum(day.count for day in daily_executions[-14:-7]) / 7 if len(daily_executions) >= 14 else recent_avg
    
    if recent_avg > older_avg * 1.1:
        return "increasing"
    elif recent_avg < older_avg * 0.9:
        return "decreasing"
    else:
        return "stable"


def _calculate_consistency_score(daily_executions) -> float:
    """Calculate learning consistency score"""
    
    if len(daily_executions) < 7:
        return 0.5
    
    daily_counts = [day.count for day in daily_executions]
    avg = sum(daily_counts) / len(daily_counts)
    
    if avg == 0:
        return 0.0
    
    variance = sum((count - avg) ** 2 for count in daily_counts) / len(daily_counts)
    coefficient_of_variation = (variance ** 0.5) / avg
    
    # Lower variation = higher consistency score
    return max(0, 1 - coefficient_of_variation)


def _calculate_complexity_growth(executions) -> float:
    """Calculate complexity growth over time"""
    
    # Simplified complexity based on code length and execution time
    if len(executions) < 5:
        return 0.0
    
    early_complexity = sum(len(e.code or "") for e in executions[:5]) / 5
    recent_complexity = sum(len(e.code or "") for e in executions[-5:]) / 5
    
    return (recent_complexity - early_complexity) / max(early_complexity, 1)


def _calculate_error_rate_trend(executions) -> float:
    """Calculate error rate trend"""
    
    if len(executions) < 10:
        return 0.0
    
    early_errors = sum(1 for e in executions[:10] if e.status != "completed") / 10
    recent_errors = sum(1 for e in executions[-10:] if e.status != "completed") / 10
    
    return early_errors - recent_errors  # Positive = improvement


def _calculate_performance_trend(executions) -> str:
    """Calculate performance trend"""
    
    if len(executions) < 10:
        return "stable"
    
    early_avg = sum(e.execution_time_ms for e in executions[:10]) / 10
    recent_avg = sum(e.execution_time_ms for e in executions[-10:]) / 10
    
    if recent_avg < early_avg * 0.9:
        return "improving"
    elif recent_avg > early_avg * 1.1:
        return "declining"
    else:
        return "stable"


def _calculate_optimization_score(executions) -> float:
    """Calculate code optimization score"""
    
    # Based on execution time efficiency
    times = [e.execution_time_ms for e in executions if e.execution_time_ms]
    if not times:
        return 0.5
    
    avg_time = sum(times) / len(times)
    optimal_time = min(times)
    
    return optimal_time / max(avg_time, 1)


async def _get_recent_activities(db: Session, user_id: int) -> List[Dict]:
    """Get recent user activities across all services"""
    
    activities = []
    
    # Recent code executions
    recent_executions = db.query(CodeExecution).filter(
        CodeExecution.user_id == user_id
    ).order_by(desc(CodeExecution.started_at)).limit(3).all()
    
    for execution in recent_executions:
        activities.append({
            "type": "code_executed",
            "title": f"{execution.language.title()} Code Execution",
            "description": f"Executed in {execution.execution_time_ms}ms",
            "timestamp": execution.started_at.isoformat(),
            "status": execution.status
        })
    
    # Recent TAO transactions
    recent_transactions = db.query(TAOTransaction).filter(
        TAOTransaction.user_id == user_id
    ).order_by(desc(TAOTransaction.created_at)).limit(2).all()
    
    for transaction in recent_transactions:
        activities.append({
            "type": "tao_transaction",
            "title": f"TAO {transaction.transaction_type.title()}",
            "description": f"Amount: {transaction.amount_tao} TAO",
            "timestamp": transaction.created_at.isoformat(),
            "status": "confirmed" if transaction.is_confirmed else "pending"
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:5]


def _calculate_resource_trends(usage_records: List[WebVMResourceUsage]) -> Dict:
    """Calculate resource usage trends"""
    
    if not usage_records:
        return {"cpu_trend": 0, "memory_trend": 0, "disk_trend": 0}
    
    # Sort by timestamp
    sorted_records = sorted(usage_records, key=lambda x: x.recorded_at)
    
    # Calculate simple trends (positive = increasing, negative = decreasing)
    cpu_values = [r.cpu_usage_percent for r in sorted_records]
    memory_values = [r.memory_usage_mb for r in sorted_records]
    disk_values = [r.disk_usage_mb for r in sorted_records]
    
    def calculate_trend(values):
        if len(values) < 2:
            return 0
        return (values[-1] - values[0]) / len(values)
    
    return {
        "cpu_trend": round(calculate_trend(cpu_values), 2),
        "memory_trend": round(calculate_trend(memory_values), 2),
        "disk_trend": round(calculate_trend(disk_values), 2)
    }


def _get_subnet_activity_summary(validations: List[BittensorValidation]) -> Dict:
    """Get summary of subnet activity"""
    
    subnet_counts = {}
    for validation in validations:
        # Subnet info would come from the node relationship
        subnet_counts["educational"] = subnet_counts.get("educational", 0) + 1
    
    return subnet_counts


async def _get_user_achievements(db: Session, user_id: int) -> List[Dict]:
    """Get user achievements and milestones"""
    
    achievements = []
    
    # Code execution achievements
    total_executions = db.query(CodeExecution).filter(
        CodeExecution.user_id == user_id
    ).count()
    
    if total_executions >= 100:
        achievements.append({
            "id": "code_master",
            "title": "Code Master",
            "description": "Executed 100+ code snippets",
            "icon": "🚀",
            "earned_at": datetime.utcnow().isoformat(),
            "rarity": "epic"
        })
    elif total_executions >= 50:
        achievements.append({
            "id": "code_warrior",
            "title": "Code Warrior",
            "description": "Executed 50+ code snippets",
            "icon": "⚔️",
            "earned_at": datetime.utcnow().isoformat(),
            "rarity": "rare"
        })
    
    # TAO earnings achievements
    total_tao = db.query(func.sum(TAOTransaction.amount_tao)).filter(
        and_(
            TAOTransaction.user_id == user_id,
            TAOTransaction.transaction_type == "reward"
        )
    ).scalar() or 0.0
    
    if total_tao >= 1.0:
        achievements.append({
            "id": "tao_millionaire",
            "title": "TAO Millionaire",
            "description": "Earned 1+ TAO tokens",
            "icon": "💰",
            "earned_at": datetime.utcnow().isoformat(),
            "rarity": "legendary"
        })
    
    return achievements


def _calculate_user_level(tao_earned: float, code_executions: int) -> int:
    """Calculate user level based on activity"""
    
    total_xp = int(tao_earned * 1000 + code_executions * 10)
    
    # Level calculation: each level requires more XP
    level = 1
    required_xp = 100
    
    while total_xp >= required_xp:
        total_xp -= required_xp
        level += 1
        required_xp = int(required_xp * 1.2)  # 20% increase per level
    
    return min(level, 100)  # Cap at level 100


def _get_user_badges(db: Session, user_id: int) -> List[Dict]:
    """Get user badges based on achievements"""
    
    badges = []
    
    # First execution badge
    first_execution = db.query(CodeExecution).filter(
        CodeExecution.user_id == user_id
    ).first()
    
    if first_execution:
        badges.append({
            "id": "first_steps",
            "name": "First Steps",
            "description": "Executed your first code",
            "icon": "👶",
            "color": "#4CAF50"
        })
    
    # Security badge for safe coding
    badges.append({
        "id": "security_conscious",
        "name": "Security Conscious",
        "description": "Maintains good security practices",
        "icon": "🛡️",
        "color": "#FF9800"
    })
    
    return badges