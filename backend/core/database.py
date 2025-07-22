from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config.settings import settings
from .database.security import (
    DatabaseSecurityConfig, 
    setup_database_security_events,
    RowLevelSecurity
)

# Secure database URL with SSL/TLS
secure_database_url = DatabaseSecurityConfig.get_secure_database_url()

# Async engine for main application
engine = create_async_engine(secure_database_url, echo=settings.ENVIRONMENT == "development", future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine for migrations and security setup
sync_engine = create_engine(
    secure_database_url.replace('postgresql+asyncpg://', 'postgresql://'),
    **DatabaseSecurityConfig.get_engine_config()
)

# Setup database security events
setup_database_security_events(sync_engine)

# Enable row-level security policies
try:
    RowLevelSecurity.enable_rls_policies(sync_engine)
except Exception as e:
    print(f"Warning: Could not enable RLS policies during startup: {e}")

# Regular sync session for security operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_db():
    """Sync database session for security operations"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
