"""
WebVM Security Hardening
Advanced security measures for browser-based virtual machines
"""

import re
import hashlib
import json
import time
import ipaddress
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from .models import WebVMInstance, CodeExecution, VMStatus, ExecutionStatus
from ...core.config.settings import settings

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for WebVM instances"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class ThreatLevel(Enum):
    """Threat classification levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityPolicy:
    """WebVM security policy configuration"""
    max_memory_mb: int
    max_disk_mb: int
    max_execution_time: int
    network_access: bool
    file_upload: bool
    internet_access: bool
    allowed_domains: List[str]
    blocked_commands: List[str]
    max_processes: int
    max_open_files: int
    syscall_restrictions: List[str]


@dataclass
class SecurityThreat:
    """Security threat detection result"""
    threat_type: str
    threat_level: ThreatLevel
    description: str
    evidence: Dict[str, Any]
    mitigation: str
    timestamp: datetime


class WebVMSecurityManager:
    """Advanced security manager for WebVM instances"""
    
    def __init__(self):
        self.security_policies = self._initialize_security_policies()
        self.threat_signatures = self._initialize_threat_signatures()
        self.network_monitor = NetworkSecurityAnalyzer()
        self.code_analyzer = CodeSecurityAnalyzer()
        self.resource_monitor = ResourceSecurityMonitor()
        self.detected_threats: List[SecurityThreat] = []
        
    def _initialize_security_policies(self) -> Dict[SecurityLevel, SecurityPolicy]:
        """Initialize security policies for different levels"""
        
        return {
            SecurityLevel.LOW: SecurityPolicy(
                max_memory_mb=512,
                max_disk_mb=1024,
                max_execution_time=30,
                network_access=True,
                file_upload=True,
                internet_access=True,
                allowed_domains=["*"],
                blocked_commands=["rm", "sudo", "su", "chmod", "chown"],
                max_processes=10,
                max_open_files=50,
                syscall_restrictions=["mount", "umount", "reboot"]
            ),
            SecurityLevel.MEDIUM: SecurityPolicy(
                max_memory_mb=256,
                max_disk_mb=512,
                max_execution_time=20,
                network_access=False,
                file_upload=True,
                internet_access=False,
                allowed_domains=["github.com", "stackoverflow.com"],
                blocked_commands=["rm", "sudo", "su", "chmod", "chown", "wget", "curl"],
                max_processes=5,
                max_open_files=25,
                syscall_restrictions=["mount", "umount", "reboot", "socket", "bind"]
            ),
            SecurityLevel.HIGH: SecurityPolicy(
                max_memory_mb=128,
                max_disk_mb=256,
                max_execution_time=10,
                network_access=False,
                file_upload=False,
                internet_access=False,
                allowed_domains=[],
                blocked_commands=["rm", "sudo", "su", "chmod", "chown", "wget", "curl", "ssh", "scp"],
                max_processes=3,
                max_open_files=10,
                syscall_restrictions=["mount", "umount", "reboot", "socket", "bind", "connect", "listen"]
            ),
            SecurityLevel.MAXIMUM: SecurityPolicy(
                max_memory_mb=64,
                max_disk_mb=128,
                max_execution_time=5,
                network_access=False,
                file_upload=False,
                internet_access=False,
                allowed_domains=[],
                blocked_commands=["*"],  # Only whitelist allowed
                max_processes=1,
                max_open_files=5,
                syscall_restrictions=["*"]  # Highly restricted
            )
        }
    
    def _initialize_threat_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threat detection signatures"""
        
        return {
            "malicious_code": {
                "patterns": [
                    r"import\s+os\s*;\s*os\.system",
                    r"subprocess\.(call|run|Popen)",
                    r"eval\s*\(",
                    r"exec\s*\(",
                    r"__import__\s*\(",
                    r"open\s*\(\s*['\"]\/etc\/passwd",
                    r"while\s+True\s*:",
                    r"fork\s*\(",
                    r"process\.spawn",
                    r"require\s*\(\s*['\"]child_process"
                ],
                "threat_level": ThreatLevel.HIGH,
                "description": "Potentially malicious code execution patterns"
            },
            "network_exploit": {
                "patterns": [
                    r"socket\.(socket|bind|listen|connect)",
                    r"urllib\.request\.urlopen",
                    r"requests\.(get|post|put|delete)",
                    r"fetch\s*\(",
                    r"XMLHttpRequest",
                    r"axios\.(get|post|put|delete)"
                ],
                "threat_level": ThreatLevel.MEDIUM,
                "description": "Network communication attempts"
            },
            "file_manipulation": {
                "patterns": [
                    r"os\.remove\s*\(",
                    r"shutil\.rmtree",
                    r"os\.rmdir",
                    r"unlink\s*\(",
                    r"fs\.unlink",
                    r"fs\.rmdir",
                    r"Files\.delete",
                    r"File\.delete"
                ],
                "threat_level": ThreatLevel.MEDIUM,
                "description": "File system manipulation attempts"
            },
            "resource_exhaustion": {
                "patterns": [
                    r"while\s+True\s*:",
                    r"for\s+.*\s+in\s+range\s*\(\s*\d{6,}",
                    r"Array\s*\(\s*\d{6,}",
                    r"malloc\s*\(\s*\d{6,}",
                    r"new\s+byte\s*\[\s*\d{6,}"
                ],
                "threat_level": ThreatLevel.HIGH,
                "description": "Potential resource exhaustion attack"
            },
            "privilege_escalation": {
                "patterns": [
                    r"sudo\s+",
                    r"su\s+",
                    r"chmod\s+777",
                    r"setuid\s*\(",
                    r"setgid\s*\(",
                    r"Process\.getRuntime"
                ],
                "threat_level": ThreatLevel.CRITICAL,
                "description": "Privilege escalation attempt"
            }
        }
    
    async def validate_vm_instance(
        self, 
        vm_instance: WebVMInstance,
        user_permissions: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """Comprehensive security validation for VM instance"""
        
        validation_result = {
            "is_secure": True,
            "security_level": SecurityLevel.MEDIUM,
            "threats_detected": [],
            "policy_violations": [],
            "recommendations": [],
            "risk_score": 0.0
        }
        
        try:
            # 1. Resource limit validation
            resource_validation = await self._validate_resource_limits(vm_instance)
            if not resource_validation["valid"]:
                validation_result["policy_violations"].extend(resource_validation["violations"])
                validation_result["risk_score"] += 0.2
            
            # 2. Network security validation
            network_validation = await self.network_monitor.validate_network_config(vm_instance)
            if network_validation["threats"]:
                validation_result["threats_detected"].extend(network_validation["threats"])
                validation_result["risk_score"] += 0.3
            
            # 3. User permission validation
            if user_permissions:
                permission_validation = await self._validate_user_permissions(vm_instance, user_permissions)
                if not permission_validation["valid"]:
                    validation_result["policy_violations"].extend(permission_validation["violations"])
                    validation_result["risk_score"] += 0.1
            
            # 4. Environment security validation
            env_validation = await self._validate_environment_security(vm_instance)
            if env_validation["threats"]:
                validation_result["threats_detected"].extend(env_validation["threats"])
                validation_result["risk_score"] += 0.2
            
            # 5. Determine security level and overall status
            validation_result["security_level"] = self._calculate_security_level(validation_result["risk_score"])
            validation_result["is_secure"] = validation_result["risk_score"] < 0.5
            
            # 6. Generate security recommendations
            validation_result["recommendations"] = self._generate_security_recommendations(validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"VM instance validation failed: {str(e)}")
            return {
                "is_secure": False,
                "security_level": SecurityLevel.HIGH,
                "threats_detected": [{"type": "validation_error", "description": str(e)}],
                "policy_violations": [],
                "recommendations": ["Manual security review required"],
                "risk_score": 1.0
            }
    
    async def analyze_code_execution(
        self, 
        code_execution: CodeExecution
    ) -> Dict[str, Any]:
        """Analyze code execution for security threats"""
        
        analysis_result = await self.code_analyzer.analyze_code_security(
            code_execution.code,
            code_execution.language,
            self.threat_signatures
        )
        
        # Store detected threats
        for threat in analysis_result.get("threats", []):
            security_threat = SecurityThreat(
                threat_type=threat["type"],
                threat_level=ThreatLevel(threat["level"]),
                description=threat["description"],
                evidence={"code_snippet": threat.get("evidence", "")},
                mitigation=threat.get("mitigation", "Block execution"),
                timestamp=datetime.utcnow()
            )
            
            self.detected_threats.append(security_threat)
            
            # Log critical threats
            if security_threat.threat_level == ThreatLevel.CRITICAL:
                logger.critical(f"Critical security threat detected: {security_threat.description}")
        
        return analysis_result
    
    async def enforce_security_policy(
        self,
        vm_instance: WebVMInstance,
        policy_level: SecurityLevel = SecurityLevel.MEDIUM
    ) -> Dict[str, Any]:
        """Enforce security policy on VM instance"""
        
        policy = self.security_policies[policy_level]
        enforcement_result = {
            "policy_applied": policy_level.value,
            "restrictions_applied": [],
            "violations_prevented": [],
            "resource_limits_set": {}
        }
        
        try:
            # 1. Apply resource limits
            resource_limits = {
                "max_memory_mb": min(vm_instance.memory_mb, policy.max_memory_mb),
                "max_disk_mb": min(vm_instance.disk_mb, policy.max_disk_mb),
                "max_execution_time": policy.max_execution_time,
                "max_processes": policy.max_processes,
                "max_open_files": policy.max_open_files
            }
            
            # Update VM instance with enforced limits
            vm_instance.memory_mb = resource_limits["max_memory_mb"]
            vm_instance.disk_mb = resource_limits["max_disk_mb"]
            
            enforcement_result["resource_limits_set"] = resource_limits
            
            # 2. Apply network restrictions
            if not policy.network_access:
                vm_instance.network_enabled = False
                enforcement_result["restrictions_applied"].append("network_disabled")
            
            # 3. Configure allowed domains
            if policy.allowed_domains and policy.allowed_domains != ["*"]:
                enforcement_result["restrictions_applied"].append(f"domain_whitelist:{len(policy.allowed_domains)}")
            
            # 4. Apply command restrictions
            if policy.blocked_commands:
                enforcement_result["restrictions_applied"].append(f"command_blacklist:{len(policy.blocked_commands)}")
            
            # 5. Apply syscall restrictions
            if policy.syscall_restrictions:
                enforcement_result["restrictions_applied"].append(f"syscall_restrictions:{len(policy.syscall_restrictions)}")
            
            logger.info(f"Security policy {policy_level.value} applied to VM {vm_instance.session_id}")
            
            return enforcement_result
            
        except Exception as e:
            logger.error(f"Failed to enforce security policy: {str(e)}")
            return {
                "policy_applied": "error",
                "error": str(e)
            }
    
    async def get_security_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive security metrics for WebVM"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_threats = [
            threat for threat in self.detected_threats
            if threat.timestamp >= cutoff_time
        ]
        
        # Categorize threats by type and level
        threat_types = {}
        threat_levels = {level.value: 0 for level in ThreatLevel}
        
        for threat in recent_threats:
            threat_types[threat.threat_type] = threat_types.get(threat.threat_type, 0) + 1
            threat_levels[threat.threat_level.value] += 1
        
        return {
            "time_period_hours": hours,
            "total_threats_detected": len(recent_threats),
            "threat_types": threat_types,
            "threat_levels": threat_levels,
            "critical_threats": threat_levels["critical"],
            "high_threats": threat_levels["high"],
            "security_incidents": len([t for t in recent_threats if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]),
            "most_common_threat": max(threat_types.keys(), key=threat_types.get) if threat_types else "none",
            "security_trend": self._calculate_security_trend(recent_threats)
        }
    
    async def _validate_resource_limits(self, vm_instance: WebVMInstance) -> Dict[str, Any]:
        """Validate resource limits against security policies"""
        
        violations = []
        
        # Check memory limits
        if vm_instance.memory_mb > 1024:  # 1GB limit
            violations.append("Memory allocation exceeds 1GB limit")
        
        # Check disk limits
        if vm_instance.disk_mb > 2048:  # 2GB limit
            violations.append("Disk allocation exceeds 2GB limit")
        
        # Check CPU core limits
        if vm_instance.cpu_cores > 2:
            violations.append("CPU core allocation exceeds 2 core limit")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    async def _validate_user_permissions(
        self, 
        vm_instance: WebVMInstance, 
        user_permissions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Validate user permissions against VM configuration"""
        
        violations = []
        
        # Check network access permissions
        if vm_instance.network_enabled and not user_permissions.get("network_access", False):
            violations.append("User lacks permission for network access")
        
        # Check file upload permissions
        if user_permissions.get("file_upload_restricted", False):
            violations.append("File upload restricted for this user")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    async def _validate_environment_security(self, vm_instance: WebVMInstance) -> Dict[str, Any]:
        """Validate environment security configuration"""
        
        threats = []
        
        # Check for dangerous environment variables
        if vm_instance.environment_variables:
            for key, value in vm_instance.environment_variables.items():
                if key.upper() in ["PATH", "LD_LIBRARY_PATH", "PYTHONPATH"] and "../" in value:
                    threats.append({
                        "type": "path_traversal",
                        "description": f"Potential path traversal in {key}",
                        "evidence": f"{key}={value}"
                    })
        
        return {"threats": threats}
    
    def _calculate_security_level(self, risk_score: float) -> SecurityLevel:
        """Calculate appropriate security level based on risk score"""
        
        if risk_score >= 0.8:
            return SecurityLevel.MAXIMUM
        elif risk_score >= 0.6:
            return SecurityLevel.HIGH
        elif risk_score >= 0.3:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _generate_security_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on validation results"""
        
        recommendations = []
        risk_score = validation_result["risk_score"]
        
        if risk_score > 0.7:
            recommendations.append("Consider applying maximum security policy")
            recommendations.append("Disable network access for this instance")
        
        if validation_result["threats_detected"]:
            recommendations.append("Review and sanitize code before execution")
            recommendations.append("Enable enhanced monitoring for this instance")
        
        if validation_result["policy_violations"]:
            recommendations.append("Adjust resource allocations to meet security policies")
        
        if not recommendations:
            recommendations.append("Security posture is acceptable for current configuration")
        
        return recommendations
    
    def _calculate_security_trend(self, threats: List[SecurityThreat]) -> str:
        """Calculate security trend based on threat history"""
        
        if not threats:
            return "stable"
        
        # Sort threats by timestamp
        sorted_threats = sorted(threats, key=lambda x: x.timestamp)
        
        # Compare first and second half
        mid_point = len(sorted_threats) // 2
        if mid_point == 0:
            return "stable"
        
        first_half = sorted_threats[:mid_point]
        second_half = sorted_threats[mid_point:]
        
        first_critical = sum(1 for t in first_half if t.threat_level == ThreatLevel.CRITICAL)
        second_critical = sum(1 for t in second_half if t.threat_level == ThreatLevel.CRITICAL)
        
        if second_critical > first_critical * 1.5:
            return "deteriorating"
        elif second_critical < first_critical * 0.5:
            return "improving"
        else:
            return "stable"


class NetworkSecurityAnalyzer:
    """Network security analysis for WebVM instances"""
    
    async def validate_network_config(self, vm_instance: WebVMInstance) -> Dict[str, Any]:
        """Validate network configuration for security threats"""
        
        threats = []
        
        # Check if network access is enabled for untrusted environments
        if vm_instance.network_enabled:
            # Check for suspicious patterns in environment variables
            if vm_instance.environment_variables:
                for key, value in vm_instance.environment_variables.items():
                    if self._is_suspicious_network_config(key, value):
                        threats.append({
                            "type": "suspicious_network_config",
                            "description": f"Suspicious network configuration in {key}",
                            "evidence": f"{key}={value[:100]}..."  # Truncate long values
                        })
        
        return {"threats": threats}
    
    def _is_suspicious_network_config(self, key: str, value: str) -> bool:
        """Check if network configuration is suspicious"""
        
        suspicious_patterns = [
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",  # IP:Port patterns
            r"proxy",
            r"tunnel",
            r"backdoor",
            r"reverse",
            r"shell"
        ]
        
        combined_string = f"{key}={value}".lower()
        return any(re.search(pattern, combined_string) for pattern in suspicious_patterns)


class CodeSecurityAnalyzer:
    """Code security analysis for WebVM execution"""
    
    async def analyze_code_security(
        self,
        code: str,
        language: str,
        threat_signatures: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze code for security threats"""
        
        threats = []
        risk_score = 0.0
        
        # Check against threat signatures
        for threat_type, signature_info in threat_signatures.items():
            for pattern in signature_info["patterns"]:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    threats.append({
                        "type": threat_type,
                        "level": signature_info["threat_level"].value,
                        "description": signature_info["description"],
                        "evidence": match.group(0),
                        "line": code[:match.start()].count('\n') + 1,
                        "mitigation": self._get_mitigation_for_threat(threat_type)
                    })
                    
                    # Increase risk score based on threat level
                    risk_multiplier = {
                        ThreatLevel.LOW.value: 0.1,
                        ThreatLevel.MEDIUM.value: 0.2,
                        ThreatLevel.HIGH.value: 0.4,
                        ThreatLevel.CRITICAL.value: 0.6
                    }
                    risk_score += risk_multiplier.get(signature_info["threat_level"].value, 0.1)
        
        # Language-specific security checks
        language_threats = await self._check_language_specific_threats(code, language)
        threats.extend(language_threats)
        
        return {
            "threats": threats,
            "risk_score": min(1.0, risk_score),
            "is_safe": len(threats) == 0 and risk_score < 0.3,
            "recommendations": self._generate_code_security_recommendations(threats)
        }
    
    async def _check_language_specific_threats(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for language-specific security threats"""
        
        threats = []
        
        if language.lower() == "python":
            threats.extend(await self._check_python_threats(code))
        elif language.lower() == "javascript":
            threats.extend(await self._check_javascript_threats(code))
        elif language.lower() in ["c", "cpp"]:
            threats.extend(await self._check_c_cpp_threats(code))
        
        return threats
    
    async def _check_python_threats(self, code: str) -> List[Dict[str, Any]]:
        """Check Python-specific security threats"""
        
        threats = []
        
        # Check for dangerous imports
        dangerous_imports = ["os", "subprocess", "sys", "importlib", "__builtin__", "builtins"]
        for module in dangerous_imports:
            if re.search(rf"import\s+{module}", code):
                threats.append({
                    "type": "dangerous_import",
                    "level": ThreatLevel.MEDIUM.value,
                    "description": f"Import of potentially dangerous module: {module}",
                    "evidence": f"import {module}",
                    "mitigation": "Review import necessity and restrict if possible"
                })
        
        return threats
    
    async def _check_javascript_threats(self, code: str) -> List[Dict[str, Any]]:
        """Check JavaScript-specific security threats"""
        
        threats = []
        
        # Check for dangerous functions
        dangerous_functions = ["eval", "setTimeout", "setInterval", "Function"]
        for func in dangerous_functions:
            if re.search(rf"{func}\s*\(", code):
                threats.append({
                    "type": "dangerous_function",
                    "level": ThreatLevel.MEDIUM.value,
                    "description": f"Use of potentially dangerous function: {func}",
                    "evidence": f"{func}(",
                    "mitigation": "Avoid dynamic code execution"
                })
        
        return threats
    
    async def _check_c_cpp_threats(self, code: str) -> List[Dict[str, Any]]:
        """Check C/C++ specific security threats"""
        
        threats = []
        
        # Check for buffer overflow risks
        dangerous_functions = ["gets", "strcpy", "strcat", "sprintf", "scanf"]
        for func in dangerous_functions:
            if re.search(rf"{func}\s*\(", code):
                threats.append({
                    "type": "buffer_overflow_risk",
                    "level": ThreatLevel.HIGH.value,
                    "description": f"Use of unsafe function: {func}",
                    "evidence": f"{func}(",
                    "mitigation": "Use safe alternatives like strncpy, snprintf"
                })
        
        return threats
    
    def _get_mitigation_for_threat(self, threat_type: str) -> str:
        """Get appropriate mitigation for threat type"""
        
        mitigations = {
            "malicious_code": "Block execution and review code",
            "network_exploit": "Disable network access",
            "file_manipulation": "Restrict file system access",
            "resource_exhaustion": "Apply strict resource limits",
            "privilege_escalation": "Run in sandboxed environment with minimal privileges"
        }
        
        return mitigations.get(threat_type, "Manual review required")
    
    def _generate_code_security_recommendations(self, threats: List[Dict[str, Any]]) -> List[str]:
        """Generate code security recommendations"""
        
        if not threats:
            return ["Code appears safe for execution"]
        
        recommendations = []
        
        # Group threats by type
        threat_types = {}
        for threat in threats:
            threat_type = threat["type"]
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
        
        for threat_type, count in threat_types.items():
            if count > 1:
                recommendations.append(f"Multiple {threat_type} threats detected - consider code review")
            else:
                recommendations.append(f"{threat_type.replace('_', ' ').title()} detected - verify necessity")
        
        # Add general recommendations
        if any(threat["level"] == ThreatLevel.CRITICAL.value for threat in threats):
            recommendations.append("CRITICAL: Block execution until threats are resolved")
        
        return recommendations


class ResourceSecurityMonitor:
    """Resource security monitoring for WebVM instances"""
    
    async def monitor_resource_security(
        self, 
        vm_instance: WebVMInstance,
        current_usage: Dict[str, float]
    ) -> Dict[str, Any]:
        """Monitor resource usage for security threats"""
        
        threats = []
        
        # Check for resource exhaustion patterns
        memory_usage_percent = (current_usage.get("memory_mb", 0) / vm_instance.memory_mb) * 100
        if memory_usage_percent > 90:
            threats.append({
                "type": "memory_exhaustion",
                "description": f"Memory usage at {memory_usage_percent:.1f}%",
                "severity": "high" if memory_usage_percent > 95 else "medium"
            })
        
        # Check CPU usage patterns
        cpu_usage = current_usage.get("cpu_percent", 0)
        if cpu_usage > 95:
            threats.append({
                "type": "cpu_exhaustion", 
                "description": f"CPU usage at {cpu_usage:.1f}%",
                "severity": "high"
            })
        
        return {
            "threats": threats,
            "resource_health": "healthy" if not threats else "at_risk"
        }


# Global instance
webvm_security_manager = WebVMSecurityManager()

# Export components
__all__ = [
    "WebVMSecurityManager",
    "SecurityLevel",
    "ThreatLevel", 
    "SecurityPolicy",
    "SecurityThreat",
    "NetworkSecurityAnalyzer",
    "CodeSecurityAnalyzer",
    "ResourceSecurityMonitor",
    "webvm_security_manager"
]