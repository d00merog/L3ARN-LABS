"""
Security Middleware
Enhanced security middleware for L3ARN Labs platform
"""

import time
import json
import hashlib
from typing import Dict, Optional, List, Callable
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Redis client for rate limiting
redis_client = redis.Redis.from_url(
    settings.CELERY_BROKER_URL, 
    decode_responses=True
)


class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        
        return {
            # Content Security Policy
            "Content-Security-Policy": " ".join([
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' wss: https: ws:",
                "media-src 'self' blob:",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'none'",
                "worker-src 'self' blob:",
                "child-src 'self' blob:"
            ]),
            
            # Prevent content type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # HSTS (HTTPS only)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Permissions policy
            "Permissions-Policy": " ".join([
                "geolocation=()",
                "microphone=()",
                "camera=()",
                "fullscreen=(self)",
                "payment=()",
                "usb=()"
            ]),
            
            # Feature policy
            "Feature-Policy": " ".join([
                "geolocation 'none'",
                "microphone 'none'", 
                "camera 'none'",
                "payment 'none'"
            ])
        }


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.rate_limits = {
            # Global limits
            "global": {"requests": 10000, "window": 3600},  # 10k requests per hour
            
            # Authentication endpoints
            "auth": {"requests": 10, "window": 300},  # 10 attempts per 5 minutes
            
            # API endpoints
            "api": {"requests": 1000, "window": 3600},  # 1k requests per hour
            
            # WebVM operations
            "webvm": {"requests": 100, "window": 3600},  # 100 VM operations per hour
            
            # Bittensor operations
            "bittensor": {"requests": 50, "window": 3600},  # 50 operations per hour
            
            # File uploads
            "upload": {"requests": 20, "window": 3600},  # 20 uploads per hour
        }
    
    def get_rate_limit_key(self, request: Request, limit_type: str) -> str:
        """Generate rate limit key"""
        
        # Get client identifier (IP or user ID)
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, 'user_id', None)
        
        if user_id:
            return f"rate_limit:{limit_type}:user:{user_id}"
        else:
            return f"rate_limit:{limit_type}:ip:{client_ip}"
    
    def check_rate_limit(self, request: Request, limit_type: str = "api") -> Dict[str, any]:
        """Check if request is within rate limits"""
        
        if limit_type not in self.rate_limits:
            limit_type = "api"
        
        limit_config = self.rate_limits[limit_type]
        key = self.get_rate_limit_key(request, limit_type)
        
        try:
            # Sliding window rate limiting using Redis
            current_time = int(time.time())
            window_start = current_time - limit_config["window"]
            
            # Remove old entries
            redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = redis_client.zcard(key)
            
            # Check if limit exceeded
            if current_requests >= limit_config["requests"]:
                return {
                    "allowed": False,
                    "limit": limit_config["requests"],
                    "remaining": 0,
                    "reset_time": current_time + limit_config["window"],
                    "retry_after": limit_config["window"]
                }
            
            # Add current request
            redis_client.zadd(key, {str(current_time): current_time})
            redis_client.expire(key, limit_config["window"])
            
            return {
                "allowed": True,
                "limit": limit_config["requests"],
                "remaining": limit_config["requests"] - current_requests - 1,
                "reset_time": current_time + limit_config["window"],
                "retry_after": 0
            }
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request if Redis is unavailable
            return {
                "allowed": True,
                "limit": limit_config["requests"],
                "remaining": limit_config["requests"],
                "reset_time": current_time + limit_config["window"],
                "retry_after": 0
            }
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address considering proxies"""
        
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.security_headers = SecurityHeaders()
        
        # Suspicious activity tracking
        self.suspicious_ips: Dict[str, Dict] = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security layers"""
        
        start_time = time.time()
        
        try:
            # 1. Basic security checks
            if not await self._basic_security_checks(request):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Request blocked by security policy"}
                )
            
            # 2. Rate limiting
            rate_limit_result = await self._check_rate_limits(request)
            if not rate_limit_result["allowed"]:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": rate_limit_result["retry_after"]
                    },
                    headers=self._get_rate_limit_headers(rate_limit_result)
                )
            
            # 3. Process request
            response = await call_next(request)
            
            # 4. Add security headers
            self._add_security_headers(response)
            
            # 5. Add rate limit headers
            self._add_rate_limit_headers(response, rate_limit_result)
            
            # 6. Log security metrics
            await self._log_security_metrics(request, response, start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            
            # Return secure error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal security error"},
                headers=self.security_headers.get_security_headers()
            )
    
    async def _basic_security_checks(self, request: Request) -> bool:
        """Perform basic security checks"""
        
        # Check for suspicious patterns
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Block known bot patterns
        suspicious_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "curl/7.0",
            "wget/1.0", "python-requests/0.0", "bot", "crawler"
        ]
        
        if any(agent in user_agent for agent in suspicious_agents):
            await self._log_suspicious_activity(request, "suspicious_user_agent")
            return False
        
        # Check for suspicious headers
        if self._has_suspicious_headers(request):
            await self._log_suspicious_activity(request, "suspicious_headers")
            return False
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
            return False
        
        return True
    
    def _has_suspicious_headers(self, request: Request) -> bool:
        """Check for suspicious request headers"""
        
        suspicious_headers = [
            "x-forwarded-host", "x-originating-ip", "x-cluster-client-ip"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log but don't block (might be legitimate proxy)
                logger.warning(f"Suspicious header detected: {header}")
        
        return False
    
    async def _check_rate_limits(self, request: Request) -> Dict[str, any]:
        """Check rate limits based on endpoint"""
        
        path = request.url.path
        
        # Determine rate limit type based on path
        if "/auth/" in path:
            limit_type = "auth"
        elif "/webvm/" in path:
            limit_type = "webvm"
        elif "/bittensor/" in path:
            limit_type = "bittensor"
        elif "/upload" in path:
            limit_type = "upload"
        else:
            limit_type = "api"
        
        return self.rate_limiter.check_rate_limit(request, limit_type)
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        
        headers = self.security_headers.get_security_headers()
        
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
    
    def _add_rate_limit_headers(self, response: Response, rate_limit_result: Dict):
        """Add rate limiting headers"""
        
        response.headers["X-RateLimit-Limit"] = str(rate_limit_result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_result["reset_time"])
    
    def _get_rate_limit_headers(self, rate_limit_result: Dict) -> Dict[str, str]:
        """Get rate limit headers for blocked requests"""
        
        return {
            "X-RateLimit-Limit": str(rate_limit_result["limit"]),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(rate_limit_result["reset_time"]),
            "Retry-After": str(rate_limit_result["retry_after"])
        }
    
    async def _log_suspicious_activity(self, request: Request, activity_type: str):
        """Log suspicious activity for monitoring"""
        
        client_ip = self.rate_limiter._get_client_ip(request)
        
        activity_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": client_ip,
            "activity_type": activity_type,
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", ""),
            "referrer": request.headers.get("referer", "")
        }
        
        # Store in Redis for analysis
        key = f"suspicious_activity:{client_ip}"
        redis_client.lpush(key, json.dumps(activity_data))
        redis_client.expire(key, 86400)  # Keep for 24 hours
        
        logger.warning(f"Suspicious activity: {json.dumps(activity_data)}")
    
    async def _log_security_metrics(self, request: Request, response: Response, start_time: float):
        """Log security and performance metrics"""
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "client_ip": self.rate_limiter._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "")[:100]  # Truncate
        }
        
        # Log to security metrics
        logger.info(f"SECURITY_METRICS: {json.dumps(metrics)}")


class InputSanitizer:
    """Input sanitization and validation"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Basic HTML tag removal (for display purposes)
        import re
        value = re.sub(r'<[^>]+>', '', value)
        
        return value.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        
        import re
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure reasonable length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


# Export key components
__all__ = [
    "SecurityMiddleware",
    "RateLimiter", 
    "SecurityHeaders",
    "InputSanitizer"
]