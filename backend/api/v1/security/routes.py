"""
Security Monitoring API Routes
Enhanced security monitoring and reporting endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from ...core.database import get_async_db
from ...auth.crud import get_current_user
from ...auth.models import User
from ...core.security.network import network_security_manager
from pydantic import BaseModel

router = APIRouter(prefix="/security", tags=["Security Monitoring"])

logger = logging.getLogger(__name__)


class SecurityMetricsResponse(BaseModel):
    """Security metrics response model"""
    time_period_hours: int
    total_events: int
    event_types: Dict[str, int]
    severity_distribution: Dict[str, int]
    unique_ip_addresses: int
    blocked_ips: int
    high_risk_events: int
    security_level: str
    recommendations: List[str]


class SecurityEventResponse(BaseModel):
    """Security event response model"""
    event_type: str
    severity: str
    user_id: Optional[int]
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    timestamp: datetime


class SecurityScanRequest(BaseModel):
    """Security scan request model"""
    scan_type: str  # 'vulnerability', 'penetration', 'compliance'
    target: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


@router.get("/metrics", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive security metrics"""
    try:
        # Only allow admin users to access security metrics
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get security metrics from network security manager
        metrics = network_security_manager.get_security_metrics(hours)
        
        # Determine overall security level
        high_risk_events = metrics["high_risk_events"]
        total_events = metrics["total_events"]
        
        if total_events == 0:
            security_level = "excellent"
        elif high_risk_events / max(total_events, 1) < 0.01:
            security_level = "good"
        elif high_risk_events / max(total_events, 1) < 0.05:
            security_level = "moderate"
        else:
            security_level = "concerning"
        
        # Generate security recommendations
        recommendations = []
        
        if metrics["blocked_ips"] > 10:
            recommendations.append("High number of blocked IPs detected - consider implementing more restrictive access controls")
        
        if high_risk_events > 50:
            recommendations.append("Multiple high-risk security events detected - review and strengthen security policies")
        
        if "suspicious_request_pattern" in metrics["event_types"]:
            recommendations.append("Suspicious request patterns detected - consider implementing additional request validation")
        
        if len(recommendations) == 0:
            recommendations.append("Security posture is good - continue monitoring")
        
        return SecurityMetricsResponse(
            time_period_hours=hours,
            total_events=metrics["total_events"],
            event_types=metrics["event_types"],
            severity_distribution=metrics["severity_distribution"],
            unique_ip_addresses=metrics["unique_ip_addresses"],
            blocked_ips=metrics["blocked_ips"],
            high_risk_events=metrics["high_risk_events"],
            security_level=security_level,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get security metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security metrics"
        )


@router.get("/events", response_model=List[SecurityEventResponse])
async def get_security_events(
    hours: int = 24,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get recent security events"""
    try:
        # Only allow admin users to access security events
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get events from network security manager
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        all_events = [
            event for event in network_security_manager.security_events
            if event.timestamp >= cutoff_time
        ]
        
        # Filter by severity if specified
        if severity:
            all_events = [event for event in all_events if event.severity == severity]
        
        # Filter by event type if specified
        if event_type:
            all_events = [event for event in all_events if event.event_type == event_type]
        
        # Sort by timestamp (most recent first) and limit
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        events = all_events[:limit]
        
        # Convert to response model
        return [
            SecurityEventResponse(
                event_type=event.event_type,
                severity=event.severity,
                user_id=event.user_id,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                details=event.details,
                timestamp=event.timestamp
            )
            for event in events
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get security events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events"
        )


@router.post("/scan")
async def initiate_security_scan(
    scan_request: SecurityScanRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Initiate security scan"""
    try:
        # Only allow admin users to initiate security scans
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Log security scan initiation
        network_security_manager.log_security_event(
            "security_scan_initiated",
            "medium",
            {
                "scan_type": scan_request.scan_type,
                "target": scan_request.target,
                "options": scan_request.options or {},
                "initiated_by": current_user.id
            },
            request,
            current_user.id
        )
        
        # Simulate security scan (in production, this would trigger actual security tools)
        scan_results = await _perform_security_scan(scan_request)
        
        return {
            "scan_id": f"scan_{int(datetime.utcnow().timestamp())}",
            "scan_type": scan_request.scan_type,
            "status": "completed",
            "results": scan_results,
            "initiated_by": current_user.id,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Security scan failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security scan failed"
        )


@router.get("/health")
async def get_security_health(
    current_user: User = Depends(get_current_user)
):
    """Get overall security health status"""
    try:
        # Get recent metrics
        metrics = network_security_manager.get_security_metrics(hours=24)
        
        # Calculate health score
        total_events = metrics["total_events"]
        high_risk_events = metrics["high_risk_events"]
        blocked_ips = metrics["blocked_ips"]
        
        # Health scoring algorithm
        health_score = 100.0
        
        # Deduct points for security issues
        if total_events > 100:
            health_score -= min(20, (total_events - 100) * 0.1)
        
        if high_risk_events > 0:
            health_score -= min(30, high_risk_events * 2)
        
        if blocked_ips > 5:
            health_score -= min(15, (blocked_ips - 5) * 1)
        
        health_score = max(0, health_score)
        
        # Determine health status
        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 75:
            health_status = "good"
        elif health_score >= 50:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "health_score": round(health_score, 1),
            "health_status": health_status,
            "metrics_summary": {
                "total_events_24h": total_events,
                "high_risk_events": high_risk_events,
                "blocked_ips": blocked_ips,
                "unique_ip_addresses": metrics["unique_ip_addresses"]
            },
            "last_updated": datetime.utcnow(),
            "recommendations": _get_health_recommendations(health_score, metrics)
        }
        
    except Exception as e:
        logger.error(f"Failed to get security health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security health"
        )


async def _perform_security_scan(scan_request: SecurityScanRequest) -> Dict[str, Any]:
    """Perform security scan (mock implementation)"""
    
    scan_type = scan_request.scan_type
    
    if scan_type == "vulnerability":
        return {
            "vulnerabilities_found": 0,
            "severity_breakdown": {"critical": 0, "high": 0, "medium": 2, "low": 3},
            "recommendations": [
                "Update dependencies to latest versions",
                "Review CORS configuration",
                "Enable additional security headers"
            ],
            "scan_duration_seconds": 45
        }
    
    elif scan_type == "penetration":
        return {
            "penetration_attempts": 50,
            "successful_attempts": 0,
            "blocked_attempts": 50,
            "security_controls_tested": [
                "Authentication bypass",
                "SQL injection",
                "XSS attacks",
                "CSRF protection",
                "Rate limiting"
            ],
            "overall_security_rating": "strong",
            "scan_duration_seconds": 180
        }
    
    elif scan_type == "compliance":
        return {
            "compliance_framework": "OWASP Top 10",
            "controls_checked": 10,
            "controls_passed": 8,
            "controls_failed": 2,
            "compliance_percentage": 80.0,
            "failed_controls": [
                "A06:2021 – Vulnerable and Outdated Components",
                "A09:2021 – Security Logging and Monitoring Failures"
            ],
            "remediation_priority": "medium"
        }
    
    return {"error": "Unknown scan type"}


def _get_health_recommendations(health_score: float, metrics: Dict[str, Any]) -> List[str]:
    """Generate health-based security recommendations"""
    
    recommendations = []
    
    if health_score < 50:
        recommendations.append("URGENT: Security posture requires immediate attention")
    
    if metrics["high_risk_events"] > 10:
        recommendations.append("Investigate and mitigate high-risk security events")
    
    if metrics["blocked_ips"] > 20:
        recommendations.append("Review IP blocking policies and consider geo-blocking")
    
    if metrics["total_events"] > 500:
        recommendations.append("Consider implementing more aggressive rate limiting")
    
    if not recommendations:
        recommendations.append("Security posture is healthy - continue monitoring")
    
    return recommendations