"""
Module: profile_memory.py

This module provides models and services for user profile storage, learning progress,
and user preferences using FastAPI and SQLAlchemy with asyncio support.

Features:
- User profile storage
- Learning progress tracking
- User preferences management

Models:
- ProfileMemory
- LearningProgress
- UserPreferences

Usage:
    Run the application using Uvicorn:
        uvicorn profile_memory:app --reload

"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from pydantic import BaseModel, validator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine and session
engine = create_async_engine(
    DATABASE_URL, echo=True,
)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Declarative base model
Base = declarative_base()

# SQLAlchemy Models
class ProfileMemory(Base):
    """
    SQLAlchemy model for storing user profile information.

    Attributes:
        id (int): Primary key.
        user_id (int): Unique user identifier.
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.
        learning_progress (LearningProgress): One-to-one relationship with LearningProgress.
        preferences (UserPreferences): One-to-one relationship with UserPreferences.
    """
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    learning_progress = relationship(
        "LearningProgress", back_populates="profile_memory", uselist=False
    )
    preferences = relationship(
        "UserPreferences", back_populates="profile_memory", uselist=False
    )

class LearningProgress(Base):
    """
    SQLAlchemy model for storing user's learning progress.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        progress_data (str): JSON string of progress data.
        updated_at (datetime): Timestamp of last update.
        profile_memory (ProfileMemory): Relationship back to ProfileMemory.
    """
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    progress_data = Column(Text)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile_memory = relationship(
        "ProfileMemory", back_populates="learning_progress"
    )

class UserPreferences(Base):
    """
    SQLAlchemy model for storing user's preferences.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        preferences_data (str): JSON string of preferences data.
        updated_at (datetime): Timestamp of last update.
        profile_memory (ProfileMemory): Relationship back to ProfileMemory.
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    preferences_data = Column(Text)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile_memory = relationship(
        "ProfileMemory", back_populates="preferences"
    )

# Pydantic Models for Input Validation
class LearningProgressCreate(BaseModel):
    progress_data: str

    @validator('progress_data')
    def validate_progress_data(cls, v):
        if not v:
            raise ValueError('progress_data must not be empty')
        return v

class UserPreferencesCreate(BaseModel):
    preferences_data: str

    @validator('preferences_data')
    def validate_preferences_data(cls, v):
        if not v:
            raise ValueError('preferences_data must not be empty')
        return v

class ProfileMemoryCreate(BaseModel):
    user_id: int
    learning_progress: Optional[LearningProgressCreate] = None
    preferences: Optional[UserPreferencesCreate] = None

    @validator('user_id')
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('user_id must be a positive integer')
        return v

# Pydantic Models for Response Output
class LearningProgressOut(BaseModel):
    progress_data: str
    updated_at: datetime

    class Config:
        orm_mode = True

class UserPreferencesOut(BaseModel):
    preferences_data: str
    updated_at: datetime

    class Config:
        orm_mode = True

class ProfileMemoryOut(BaseModel):
    user_id: int
    created_at: datetime
    updated_at: datetime
    learning_progress: Optional[LearningProgressOut] = None
    preferences: Optional[UserPreferencesOut] = None

    class Config:
        orm_mode = True

# Repository Classes
class ProfileMemoryRepository:
    """
    Repository class for ProfileMemory operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session

    async def get_profile_by_user_id(self, user_id: int) -> Optional[ProfileMemory]:
        """
        Get a profile by user_id.

        Args:
            user_id (int): The user ID.

        Returns:
            Optional[ProfileMemory]: The profile if found, else None.

        Raises:
            SQLAlchemyError: If a database error occurs.

        >>> import asyncio
        >>> async def test_get_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.get_profile_by_user_id(1)
        ...         assert profile is None or profile.user_id == 1
        >>> asyncio.run(test_get_profile())
        """
        try:
            result = await self.session.execute(
                select(ProfileMemory).where(ProfileMemory.user_id == user_id)
            )
            profile = result.scalars().first()
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error getting profile by user_id {user_id}: {e}")
            raise

    async def create_profile(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new profile with associated learning progress and preferences.

        Args:
            profile_data (ProfileMemoryCreate): Profile data.

        Returns:
            ProfileMemory: The created profile.

        Raises:
            SQLAlchemyError: If a database error occurs.

        >>> import asyncio
        >>> async def test_create_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile_data = ProfileMemoryCreate(
        ...             user_id=1,
        ...             learning_progress=LearningProgressCreate(progress_data="{'lesson':1}"),
        ...             preferences=UserPreferencesCreate(preferences_data="{'theme':'dark'}")
        ...         )
        ...         profile = await repo.create_profile(profile_data)
        ...         assert profile.user_id == 1
        >>> asyncio.run(test_create_profile())
        """
        try:
            profile = ProfileMemory(user_id=profile_data.user_id)

            if profile_data.learning_progress:
                learning_progress = LearningProgress(
                    progress_data=profile_data.learning_progress.progress_data,
                    profile_memory=profile
                )
                self.session.add(learning_progress)

            if profile_data.preferences:
                preferences = UserPreferences(
                    preferences_data=profile_data.preferences.preferences_data,
                    profile_memory=profile
                )
                self.session.add(preferences)

            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error creating profile: {e}")
            await self.session.rollback()
            raise

# Dependency Injection
async def get_session() -> AsyncSession:
    """
    Dependency to provide an AsyncSession.

    Yields:
        AsyncSession: The database session.
    """
    async with async_session() as session:
        yield session

# Service Classes
class ProfileMemoryService:
    """
    Service class for business logic related to ProfileMemory.
    """

    def __init__(self, repository: ProfileMemoryRepository):
        """
        Initialize the ProfileMemoryService.

        Args:
            repository (ProfileMemoryRepository): The repository instance.

        """
        self.repository = repository

    async def get_profile(self, user_id: int) -> Optional[ProfileMemory]:
        """
        Get profile for a given user_id.

        Args:
            user_id (int): The user ID.

        Returns:
            Optional[ProfileMemory]: The profile if found, else None.

        >>> import asyncio
        >>> async def test_service_get_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         service = ProfileMemoryService(repo)
        ...         profile = await service.get_profile(1)
        ...         assert profile is None or profile.user_id == 1
        >>> asyncio.run(test_service_get_profile())
        """
        return await self.repository.get_profile_by_user_id(user_id)

    async def create_profile(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new profile.

        Args:
            profile_data (ProfileMemoryCreate): The profile data.

        Returns:
            ProfileMemory: The created profile.

        Raises:
            ValueError: If user_id is invalid.

        >>> import asyncio
        >>> async def test_service_create_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         service = ProfileMemoryService(repo)
        ...         profile_data = ProfileMemoryCreate(
        ...             user_id=2,
        ...             learning_progress=LearningProgressCreate(progress_data="{'lesson':2}"),
        ...             preferences=UserPreferencesCreate(preferences_data="{'theme':'light'}")
        ...         )
        ...         profile = await service.create_profile(profile_data)
        ...         assert profile.user_id == 2
        >>> asyncio.run(test_service_create_profile())
        """
        if profile_data.user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        return await self.repository.create_profile(profile_data)

# FastAPI Application
app = FastAPI()

# CORS middleware (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event Handlers
@app.on_event("startup")
async def on_startup():
    """
    Event handler for startup. Initializes the database models.
    """
    await init_models()

# Initialize database models
async def init_models():
    """
    Initialize database models (create tables).

    >>> import asyncio
    >>> asyncio.run(init_models())
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# API Endpoints
@app.post("/profiles/", response_model=ProfileMemoryOut)
async def create_profile_view(
    profile_data: ProfileMemoryCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    API endpoint to create a new profile.

    Args:
        profile_data (ProfileMemoryCreate): The profile data from the request body.
        session (AsyncSession): Database session (provided by dependency).

    Returns:
        ProfileMemoryOut: The created profile.

    Raises:
        HTTPException: If an error occurs during creation.
    """
    repository = ProfileMemoryRepository(session)
    service = ProfileMemoryService(repository)
    try:
        profile = await service.create_profile(profile_data)
        return profile
    except Exception as e:
        logger.error(f"Error creating profile via API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profiles/{user_id}", response_model=ProfileMemoryOut)
async def get_profile_view(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    API endpoint to retrieve a profile by user_id.

    Args:
        user_id (int): The user ID from the path.
        session (AsyncSession): Database session (provided by dependency).

    Returns:
        ProfileMemoryOut: The profile data.

    Raises:
        HTTPException: If the profile is not found.
    """
    repository = ProfileMemoryRepository(session)
    service = ProfileMemoryService(repository)
    profile = await service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# Run with: uvicorn profile_memory:app --reload