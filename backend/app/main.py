"""
FastAPI Backend with Advanced Features
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .database import get_db, init_db
from .routes import auth, users, courses, lessons
from .core import settings

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        yield
    finally:
        # Cleanup resources
        logger.info("Shutting down application")

app = FastAPI(
    title="L3ARN-LABS API",
    description="Advanced learning platform with async operations and caching",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS with security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with dependency injection
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    courses.router,
    prefix="/api/courses",
    tags=["Courses"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    lessons.router,
    prefix="/api/lessons",
    tags=["Lessons"],
    dependencies=[Depends(get_db)]
)

@app.get("/", tags=["Health"])
async def read_root():
    """Root endpoint with API information"""
    return {
        "app": "L3ARN-LABS API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with system status"""
    try:
        # Check database connection
        db = next(get_db())
        await db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
