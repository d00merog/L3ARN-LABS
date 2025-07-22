"""
Database Security Configuration
Enhanced security measures for database connections and operations
"""

import ssl
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import hashlib
import json

from ..config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseSecurityConfig:
    """Enhanced database security configuration"""
    
    @staticmethod
    def get_secure_database_url() -> str:
        """Get database URL with SSL/TLS configuration"""
        
        base_url = settings.DATABASE_URL
        
        # Add SSL requirements for production
        if settings.ENVIRONMENT == "production":
            if "?" in base_url:
                return f"{base_url}&sslmode=require&sslcert=/etc/ssl/certs/client-cert.pem&sslkey=/etc/ssl/private/client-key.pem&sslrootcert=/etc/ssl/certs/ca-cert.pem"
            else:
                return f"{base_url}?sslmode=require&sslcert=/etc/ssl/certs/client-cert.pem&sslkey=/etc/ssl/private/client-key.pem&sslrootcert=/etc/ssl/certs/ca-cert.pem"
        
        # Require SSL for staging
        elif settings.ENVIRONMENT == "staging":
            if "?" in base_url:
                return f"{base_url}&sslmode=require"
            else:
                return f"{base_url}?sslmode=require"
        
        # Development can use prefer (fallback to non-SSL)
        else:
            if "?" in base_url:
                return f"{base_url}&sslmode=prefer"
            else:
                return f"{base_url}?sslmode=prefer"
    
    @staticmethod
    def get_engine_config() -> Dict[str, Any]:
        """Get secure engine configuration"""
        
        return {
            "poolclass": QueuePool,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
            "pool_reset_on_return": "commit",
            "connect_args": {
                "options": "-c default_transaction_isolation=read_committed",
                "application_name": "l3arn_labs_backend",
                "connect_timeout": 10,
            },
            "echo": settings.ENVIRONMENT == "development",
            "echo_pool": settings.ENVIRONMENT == "development",
            "future": True
        }


class DatabaseAuditLogger:
    """Database audit logging for security compliance"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger("database_audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Create file handler for audit logs
        handler = logging.FileHandler("/var/log/l3arn-labs/database_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
    
    def log_query(self, query: str, parameters: Optional[Dict] = None, 
                  user_id: Optional[int] = None, session_id: Optional[str] = None):
        """Log database query for audit purposes"""
        
        # Create query hash for privacy (don't log actual sensitive data)
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": query_hash,
            "query_type": self._get_query_type(query),
            "user_id": user_id,
            "session_id": session_id,
            "parameter_count": len(parameters) if parameters else 0
        }
        
        # Only log sensitive operations
        if self._is_sensitive_operation(query):
            self.audit_logger.info(f"DB_AUDIT: {json.dumps(audit_data)}")
    
    def log_connection(self, event_type: str, connection_info: Dict[str, Any]):
        """Log database connection events"""
        
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "database": connection_info.get("database"),
            "user": connection_info.get("user"),
            "host": connection_info.get("host"),
            "port": connection_info.get("port")
        }
        
        self.audit_logger.info(f"DB_CONNECTION: {json.dumps(audit_data)}")
    
    def _get_query_type(self, query: str) -> str:
        """Determine query type from SQL"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith("select"):
            return "SELECT"
        elif query_lower.startswith("insert"):
            return "INSERT"
        elif query_lower.startswith("update"):
            return "UPDATE"
        elif query_lower.startswith("delete"):
            return "DELETE"
        elif query_lower.startswith("create"):
            return "CREATE"
        elif query_lower.startswith("drop"):
            return "DROP"
        elif query_lower.startswith("alter"):
            return "ALTER"
        else:
            return "OTHER"
    
    def _is_sensitive_operation(self, query: str) -> bool:
        """Check if query involves sensitive operations"""
        sensitive_operations = [
            "insert", "update", "delete", "drop", "alter", "create",
            "grant", "revoke", "truncate"
        ]
        
        query_lower = query.lower()
        return any(op in query_lower for op in sensitive_operations)


class RowLevelSecurity:
    """Row-level security implementation for sensitive data"""
    
    @staticmethod
    def enable_rls_policies(engine: Engine):
        """Enable row-level security policies"""
        
        rls_policies = [
            # User data access policy
            """
            CREATE POLICY user_data_policy ON users
            USING (id = current_setting('app.current_user_id')::integer);
            """,
            
            # Course access policy
            """
            CREATE POLICY course_access_policy ON courses  
            USING (
                is_public = true OR 
                created_by = current_setting('app.current_user_id')::integer OR
                id IN (
                    SELECT course_id FROM user_course_enrollments 
                    WHERE user_id = current_setting('app.current_user_id')::integer
                )
            );
            """,
            
            # WebVM instance policy
            """
            CREATE POLICY webvm_user_policy ON webvm_instances
            USING (user_id = current_setting('app.current_user_id')::integer);
            """,
            
            # TAO transaction policy
            """
            CREATE POLICY tao_transaction_policy ON tao_transactions
            USING (user_id = current_setting('app.current_user_id')::integer);
            """
        ]
        
        try:
            with engine.connect() as conn:
                # Enable RLS on sensitive tables
                sensitive_tables = [
                    "users", "courses", "webvm_instances", 
                    "tao_transactions", "code_executions",
                    "webvm_files", "bittensor_validations"
                ]
                
                for table in sensitive_tables:
                    conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"))
                
                # Create policies
                for policy in rls_policies:
                    try:
                        conn.execute(text(policy))
                    except Exception as e:
                        # Policy might already exist
                        logger.warning(f"RLS policy creation warning: {e}")
                
                conn.commit()
                logger.info("Row-level security policies enabled successfully")
                
        except Exception as e:
            logger.error(f"Failed to enable RLS policies: {e}")


class DatabaseEncryption:
    """Database field encryption for sensitive data"""
    
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key.encode()
    
    def encrypt_field(self, value: str) -> str:
        """Encrypt sensitive field value"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from encryption key
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.encryption_key).digest()
            )
            
            fernet = Fernet(key)
            encrypted_value = fernet.encrypt(value.encode())
            
            return base64.b64encode(encrypted_value).decode()
            
        except Exception as e:
            logger.error(f"Field encryption failed: {e}")
            raise
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt sensitive field value"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from encryption key
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.encryption_key).digest()
            )
            
            fernet = Fernet(key)
            encrypted_data = base64.b64decode(encrypted_value.encode())
            decrypted_value = fernet.decrypt(encrypted_data)
            
            return decrypted_value.decode()
            
        except Exception as e:
            logger.error(f"Field decryption failed: {e}")
            raise


# Global instances
audit_logger = DatabaseAuditLogger()
db_encryption = DatabaseEncryption(settings.API_KEY_ENCRYPTION_KEY)


def setup_database_security_events(engine: Engine):
    """Setup database security event listeners"""
    
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        """Handle database connection events"""
        
        connection_info = {
            "database": dbapi_connection.info.get("database"),
            "user": dbapi_connection.info.get("user"), 
            "host": dbapi_connection.info.get("host"),
            "port": dbapi_connection.info.get("port")
        }
        
        audit_logger.log_connection("CONNECT", connection_info)
        
        # Set connection-level security settings
        with dbapi_connection.cursor() as cursor:
            # Set statement timeout
            cursor.execute("SET statement_timeout = '30s'")
            
            # Set lock timeout
            cursor.execute("SET lock_timeout = '10s'")
            
            # Set application name for monitoring
            cursor.execute("SET application_name = 'l3arn_labs_backend'")
    
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Audit queries before execution"""
        
        # Get user context if available
        user_id = getattr(context, 'user_id', None)
        session_id = getattr(context, 'session_id', None)
        
        audit_logger.log_query(statement, parameters, user_id, session_id)
    
    logger.info("Database security events configured successfully")


@contextmanager
def get_secure_connection(engine: Engine, user_id: Optional[int] = None):
    """Get database connection with user context for RLS"""
    
    with engine.connect() as conn:
        try:
            # Set user context for RLS
            if user_id:
                conn.execute(text(f"SET app.current_user_id = '{user_id}'"))
            
            yield conn
            
        finally:
            # Clear user context
            try:
                conn.execute(text("RESET app.current_user_id"))
            except:
                pass  # Context might not be set


def validate_database_security() -> Dict[str, bool]:
    """Validate database security configuration"""
    
    security_checks = {
        "ssl_enabled": False,
        "rls_enabled": False,
        "audit_logging": False,
        "connection_limits": False,
        "encryption_available": False
    }
    
    try:
        # Create test engine to check configuration
        test_engine = create_engine(
            DatabaseSecurityConfig.get_secure_database_url(),
            **DatabaseSecurityConfig.get_engine_config()
        )
        
        with test_engine.connect() as conn:
            # Check SSL connection
            result = conn.execute(text("SELECT ssl_is_used()"))
            security_checks["ssl_enabled"] = result.scalar()
            
            # Check RLS on users table
            result = conn.execute(text(
                "SELECT relrowsecurity FROM pg_class WHERE relname = 'users'"
            ))
            row = result.fetchone()
            security_checks["rls_enabled"] = row[0] if row else False
            
            # Check connection limits
            result = conn.execute(text("SHOW max_connections"))
            max_conn = int(result.scalar())
            security_checks["connection_limits"] = max_conn > 0
            
            # Check if audit logging is functional
            security_checks["audit_logging"] = audit_logger.audit_logger.handlers != []
            
            # Check encryption availability
            try:
                from cryptography.fernet import Fernet
                security_checks["encryption_available"] = True
            except ImportError:
                security_checks["encryption_available"] = False
        
        logger.info(f"Database security validation: {security_checks}")
        
    except Exception as e:
        logger.error(f"Database security validation failed: {e}")
    
    return security_checks


# Export key components
__all__ = [
    "DatabaseSecurityConfig",
    "DatabaseAuditLogger", 
    "RowLevelSecurity",
    "DatabaseEncryption",
    "setup_database_security_events",
    "get_secure_connection",
    "validate_database_security",
    "audit_logger",
    "db_encryption"
]