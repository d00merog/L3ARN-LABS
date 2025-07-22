"""
Network Security Enhancements
Advanced network security for encrypted communications and API protection
"""

import hmac
import hashlib
import json
import time
import secrets
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from fastapi import Request, Response, HTTPException, status
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_type: str
    severity: str
    user_id: Optional[int]
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    timestamp: datetime


class NetworkSecurityManager:
    """Advanced network security manager for API protection"""
    
    def __init__(self):
        self.blocked_ips: set = set()
        self.suspicious_ips: Dict[str, List[datetime]] = {}
        self.security_events: List[SecurityEvent] = []
        self.encryption_keys: Dict[str, str] = {}
        
    def validate_request_signature(self, request: Request, secret_key: str) -> bool:
        """Validate HMAC signature of incoming requests"""
        try:
            # Get signature from header
            signature_header = request.headers.get('X-Signature')
            if not signature_header:
                return False
            
            # Extract timestamp and signature
            parts = signature_header.split(',')
            if len(parts) != 2:
                return False
            
            timestamp_str = parts[0].split('=')[1]
            signature = parts[1].split('=')[1]
            
            # Check timestamp (must be within 5 minutes)
            request_time = datetime.fromtimestamp(int(timestamp_str))
            if datetime.utcnow() - request_time > timedelta(minutes=5):
                return False
            
            # Calculate expected signature
            body = await request.body() if hasattr(request, 'body') else b''
            payload = f"{timestamp_str}.{body.decode('utf-8') if body else ''}"
            expected_signature = hmac.new(
                secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature validation failed: {str(e)}")
            return False
    
    def detect_anomalous_behavior(self, request: Request, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Detect anomalous network behavior patterns"""
        
        client_ip = getattr(request.client, 'host', 'unknown')
        user_agent = request.headers.get('user-agent', '')
        
        anomalies = []
        risk_score = 0.0
        
        # 1. Check for suspicious IP patterns
        if self._is_suspicious_ip(client_ip):
            anomalies.append("suspicious_ip_pattern")
            risk_score += 0.3
        
        # 2. Check request rate from this IP
        current_time = datetime.utcnow()
        if client_ip not in self.suspicious_ips:
            self.suspicious_ips[client_ip] = []
        
        # Clean old entries (older than 1 hour)
        self.suspicious_ips[client_ip] = [
            req_time for req_time in self.suspicious_ips[client_ip]
            if current_time - req_time < timedelta(hours=1)
        ]
        
        self.suspicious_ips[client_ip].append(current_time)
        
        # Check if rate exceeds threshold
        recent_requests = len([
            req_time for req_time in self.suspicious_ips[client_ip]
            if current_time - req_time < timedelta(minutes=10)
        ])
        
        if recent_requests > 100:  # More than 100 requests in 10 minutes
            anomalies.append("high_request_rate")
            risk_score += 0.4
        
        # 3. Check for suspicious user agent patterns
        if self._is_suspicious_user_agent(user_agent):
            anomalies.append("suspicious_user_agent")
            risk_score += 0.2
        
        # 4. Check for geographic anomalies (simplified)
        if self._is_suspicious_geographic_location(client_ip):
            anomalies.append("suspicious_location")
            risk_score += 0.3
        
        # 5. Check request pattern anomalies
        if self._detect_request_pattern_anomalies(request):
            anomalies.append("suspicious_request_pattern")
            risk_score += 0.3
        
        return {
            "anomalies": anomalies,
            "risk_score": min(1.0, risk_score),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": current_time
        }
    
    def generate_secure_session_token(self, user_id: int, additional_data: Dict[str, Any] = None) -> str:
        """Generate secure session token with encryption"""
        
        # Create session data
        session_data = {
            "user_id": user_id,
            "created_at": int(time.time()),
            "nonce": secrets.token_hex(16),
            **(additional_data or {})
        }
        
        # Serialize and encrypt
        json_data = json.dumps(session_data, sort_keys=True)
        encrypted_token = self._encrypt_data(json_data)
        
        return encrypted_token
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decrypt session token"""
        try:
            # Decrypt token
            decrypted_data = self._decrypt_data(token)
            session_data = json.loads(decrypted_data)
            
            # Check expiration (24 hours)
            created_at = session_data.get("created_at", 0)
            if time.time() - created_at > 86400:  # 24 hours
                return None
            
            return session_data
            
        except Exception as e:
            logger.error(f"Session token validation failed: {str(e)}")
            return None
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        request: Request,
        user_id: Optional[int] = None
    ) -> None:
        """Log security events for monitoring and analysis"""
        
        client_ip = getattr(request.client, 'host', 'unknown')
        user_agent = request.headers.get('user-agent', '')
        
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        self.security_events.append(event)
        
        # Log to system logger
        logger.warning(
            f"Security Event: {event_type} (Severity: {severity}) - "
            f"IP: {client_ip}, User: {user_id}, Details: {details}"
        )
        
        # Keep only last 1000 events in memory
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def get_security_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get security metrics for the specified time period"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_events = [
            event for event in self.security_events
            if event.timestamp >= cutoff_time
        ]
        
        # Categorize events
        event_types = {}
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        ip_addresses = set()
        
        for event in recent_events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
            ip_addresses.add(event.ip_address)
        
        return {
            "time_period_hours": hours,
            "total_events": len(recent_events),
            "event_types": event_types,
            "severity_distribution": severity_counts,
            "unique_ip_addresses": len(ip_addresses),
            "blocked_ips": len(self.blocked_ips),
            "high_risk_events": len([e for e in recent_events if e.severity in ["high", "critical"]])
        }
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address shows suspicious patterns"""
        
        # Check if IP is in block list
        if ip in self.blocked_ips:
            return True
        
        # Simple heuristics for suspicious IPs
        suspicious_patterns = [
            ip.startswith("10.0.0."),  # Internal network (suspicious for external API)
            ip.startswith("192.168."),  # Private network
            ip == "127.0.0.1",         # Localhost
            ip.count('.') != 3,        # Invalid IPv4 format
        ]
        
        return any(suspicious_patterns)
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check for suspicious user agent strings"""
        
        suspicious_agents = [
            "curl", "wget", "python-requests", "bot", "crawler",
            "spider", "scraper", "", "null", "undefined"
        ]
        
        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)
    
    def _is_suspicious_geographic_location(self, ip: str) -> bool:
        """Check for suspicious geographic locations (simplified)"""
        
        # In production, this would use a GeoIP service
        # For now, we'll use simple heuristics
        
        # Check for known proxy/VPN IP ranges (simplified)
        proxy_indicators = [
            ip.startswith("192.0.2."),    # RFC3330 test range
            ip.startswith("198.51.100."), # RFC3330 test range
            ip.startswith("203.0.113."),  # RFC3330 test range
        ]
        
        return any(proxy_indicators)
    
    def _detect_request_pattern_anomalies(self, request: Request) -> bool:
        """Detect anomalous request patterns"""
        
        # Check for suspicious request characteristics
        anomalies = []
        
        # Check for unusual headers
        headers = dict(request.headers)
        if len(headers) > 20:  # Too many headers
            anomalies.append("excessive_headers")
        
        # Check for suspicious header values
        for header_name, header_value in headers.items():
            if len(header_value) > 1000:  # Excessively long header
                anomalies.append("long_header_value")
                break
        
        # Check request method and path patterns
        method = request.method
        path = str(request.url.path)
        
        # Suspicious path patterns
        suspicious_paths = [
            "/.env", "/config", "/admin", "/.git",
            "/wp-admin", "/phpmyadmin", "/.aws"
        ]
        
        if any(sus_path in path for sus_path in suspicious_paths):
            anomalies.append("suspicious_path")
        
        return len(anomalies) > 0
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using simple XOR encryption (replace with proper encryption in production)"""
        
        # Generate or reuse encryption key
        key = "secure_key_2024"  # In production, use proper key management
        
        encrypted = []
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted.append(chr(ord(char) ^ ord(key_char)))
        
        encrypted_str = ''.join(encrypted)
        
        # Base64 encode for safe transport (simplified)
        import base64
        return base64.b64encode(encrypted_str.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data (companion to _encrypt_data)"""
        
        import base64
        
        # Decode from base64
        encrypted_str = base64.b64decode(encrypted_data.encode()).decode()
        
        # Decrypt using XOR
        key = "secure_key_2024"
        
        decrypted = []
        for i, char in enumerate(encrypted_str):
            key_char = key[i % len(key)]
            decrypted.append(chr(ord(char) ^ ord(key_char)))
        
        return ''.join(decrypted)


# Global instance
network_security_manager = NetworkSecurityManager()


# Middleware for network security
async def network_security_middleware(request: Request, call_next):
    """Network security middleware for enhanced protection"""
    
    try:
        # Detect anomalous behavior
        anomaly_result = network_security_manager.detect_anomalous_behavior(request)
        
        # Block high-risk requests
        if anomaly_result["risk_score"] > 0.8:
            network_security_manager.log_security_event(
                "high_risk_request_blocked",
                "high",
                anomaly_result,
                request
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Request blocked due to security concerns"
            )
        
        # Log medium-risk requests for monitoring
        elif anomaly_result["risk_score"] > 0.5:
            network_security_manager.log_security_event(
                "medium_risk_request",
                "medium", 
                anomaly_result,
                request
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Network security middleware error: {str(e)}")
        # Continue processing request even if security checks fail
        return await call_next(request)


# Export components
__all__ = [
    "NetworkSecurityManager",
    "SecurityEvent", 
    "network_security_manager",
    "network_security_middleware"
]