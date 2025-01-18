"""
Module: profile_memory.py

This module provides asynchronous operations for managing user profiles, including learning progress 
and user preferences, using SQLAlchemy ORM and Pydantic for data validation.

Key features:
- User profile storage
- Learning progress management
- User preferences handling

Architecture patterns:
- Repository pattern for database interactions
- Dependency injection via FastAPI's dependency system
- Asynchronous operations using async/await syntax

Best practices:
- Proper imports and type hints
- Comprehensive docstrings and comments
- Error handling and logging
- Input validation and business logic enforcement
- Async/await patterns where appropriate
- Unit tests (as doctest in docstrings)
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.future import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy base class
Base = declarative_base()

# Database URL for AsyncIO (Using SQLite for demonstration)
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# SQLAlchemy ORM models
class ProfileMemory(Base):
    """
    ORM model for user profile memory.

    Attributes:
        id (int): Primary key.
        user_id (int): Unique user identifier.
        created_at (datetime): Timestamp of profile creation.
        learning_progress (LearningProgress): One-to-one relationship with LearningProgress.
        preferences (UserPreferences): One-to-one relationship with UserPreferences.
    """
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    learning_progress = relationship("LearningProgress", back_populates="profile", uselist=False)
    preferences = relationship("UserPreferences", back_populates="profile", uselist=False)


class LearningProgress(Base):
    """
    ORM model for learning progress.

    Attributes:
        id (int): Primary key.
        profile_id (int): Foreign key to ProfileMemory.
        progress_data (str): Data representing learning progress.
        last_updated (datetime): Timestamp of last update.
        profile (ProfileMemory): Relationship back to ProfileMemory.
    """
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), nullable=False)
    progress_data = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    profile = relationship("ProfileMemory", back_populates="learning_progress")


class UserPreferences(Base):
    """
    ORM model for user preferences.

    Attributes:
        id (int): Primary key.
        profile_id (int): Foreign key to ProfileMemory.
        preferences_data (str): Data representing user preferences.
        last_updated (datetime): Timestamp of last update.
        profile (ProfileMemory): Relationship back to ProfileMemory.
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), nullable=False)
    preferences_data = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    profile = relationship("ProfileMemory", back_populates="preferences")


# Pydantic models for data validation
class LearningProgressBaseSchema(BaseModel):
    """
    Base schema for learning progress validation.

    Attributes:
        progress_data (str): Data representing learning progress.
    """
    progress_data: str

    @validator('progress_data')
    def validate_progress_data(cls, v):
        if not v:
            raise ValueError('progress_data cannot be empty')
        return v


class UserPreferencesBaseSchema(BaseModel):
    """
    Base schema for user preferences validation.

    Attributes:
        preferences_data (str): Data representing user preferences.
    """
    preferences_data: str

    @validator('preferences_data')
    def validate_preferences_data(cls, v):
        if not v:
            raise ValueError('preferences_data cannot be empty')
        return v


class ProfileMemoryBaseSchema(BaseModel):
    """
    Base schema for profile memory validation.

    Attributes:
        user_id (int): Unique user identifier.
    """
    user_id: int

    @validator('user_id')
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('user_id must be a positive integer')
        return v


class LearningProgressCreateSchema(LearningProgressBaseSchema):
    """
    Schema for creating learning progress.
    """
    pass


class UserPreferencesCreateSchema(UserPreferencesBaseSchema):
    """
    Schema for creating user preferences.
    """
    pass


class ProfileMemoryCreateSchema(ProfileMemoryBaseSchema):
    """
    Schema for creating profile memory.

    Attributes:
        learning_progress (Optional[LearningProgressCreateSchema]): Learning progress data.
        preferences (Optional[UserPreferencesCreateSchema]): User preferences data.
    """
    learning_progress: Optional[LearningProgressCreateSchema] = None
    preferences: Optional[UserPreferencesCreateSchema] = None


class LearningProgressSchema(LearningProgressBaseSchema):
    """
    Schema for returning learning progress data.

    Attributes:
        id (int): Unique identifier.
        last_updated (datetime): Timestamp of last update.
    """
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True


class UserPreferencesSchema(UserPreferencesBaseSchema):
    """
    Schema for returning user preferences data.

    Attributes:
        id (int): Unique identifier.
        last_updated (datetime): Timestamp of last update.
    """
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True


class ProfileMemorySchema(ProfileMemoryBaseSchema):
    """
    Schema for returning profile memory data.

    Attributes:
        id (int): Unique identifier.
        created_at (datetime): Timestamp of creation.
        learning_progress (Optional[LearningProgressSchema]): Learning progress data.
        preferences (Optional[UserPreferencesSchema]): User preferences data.
    """
    id: int
    created_at: datetime
    learning_progress: Optional[LearningProgressSchema] = None
    preferences: Optional[UserPreferencesSchema] = None

    class Config:
        orm_mode = True


# Repository pattern for database interactions
class ProfileMemoryRepository:
    """
    Repository for managing ProfileMemory data.

    Methods:
        get_profile: Retrieve a profile by user_id.
        create_profile: Create a new profile.
        update_profile: Update an existing profile.
        delete_profile: Delete a profile.
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_profile(self, user_id: int) -> Optional[ProfileMemory]:
        """
        Get a profile by user_id.

        Args:
            user_id (int): User ID.

        Returns:
            Optional[ProfileMemory]: ProfileMemory instance or None if not found.

        Raises:
            Exception: Database error.

        Doctest:
        >>> import asyncio
        >>> async def test_get_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.get_profile(999)
        ...         assert profile is None
        >>> asyncio.run(test_get_profile())
        """
        try:
            result = await self.db_session.execute(
                select(ProfileMemory).where(ProfileMemory.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving profile: {e}")
            raise

    async def create_profile(self, profile_data: ProfileMemoryCreateSchema) -> ProfileMemory:
        """
        Create a new profile.

        Args:
            profile_data (ProfileMemoryCreateSchema): Profile data.

        Returns:
            ProfileMemory: Created ProfileMemory instance.

        Raises:
            HTTPException: If profile creation fails.

        Doctest:
        >>> import asyncio
        >>> async def test_create_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile_data = ProfileMemoryCreateSchema(
        ...             user_id=1,
        ...             learning_progress=LearningProgressCreateSchema(progress_data="Chapter 1"),
        ...             preferences=UserPreferencesCreateSchema(preferences_data="Dark Mode")
        ...         )
        ...         profile = await repo.create_profile(profile_data)
        ...         assert profile.user_id == 1
        ...         assert profile.learning_progress.progress_data == "Chapter 1"
        ...         assert profile.preferences.preferences_data == "Dark Mode"
        ...         print("Test passed!")
        >>> asyncio.run(test_create_profile())
        Test passed!
        """
        new_profile = ProfileMemory(user_id=profile_data.user_id)

        # Handle LearningProgress
        if profile_data.learning_progress:
            learning_progress = LearningProgress(
                progress_data=profile_data.learning_progress.progress_data,
                profile=new_profile
            )
            new_profile.learning_progress = learning_progress

        # Handle UserPreferences
        if profile_data.preferences:
            preferences = UserPreferences(
                preferences_data=profile_data.preferences.preferences_data,
                profile=new_profile
            )
            new_profile.preferences = preferences

        self.db_session.add(new_profile)
        try:
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating profile: {e}")
            raise HTTPException(status_code=500, detail="Could not create profile")

        await self.db_session.refresh(new_profile)
        return new_profile

    async def update_profile(self, user_id: int, profile_data: ProfileMemoryCreateSchema) -> ProfileMemory:
        """
        Update an existing profile.

        Args:
            user_id (int): User ID.
            profile_data (ProfileMemoryCreateSchema): Profile data.

        Returns:
            ProfileMemory: Updated ProfileMemory instance.

        Raises:
            HTTPException: If profile not found or update fails.

        Doctest:
        >>> import asyncio
        >>> async def test_update_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile_data = ProfileMemoryCreateSchema(
        ...             user_id=1,
        ...             learning_progress=LearningProgressCreateSchema(progress_data="Chapter 2"),
        ...             preferences=UserPreferencesCreateSchema(preferences_data="Light Mode")
        ...         )
        ...         profile = await repo.update_profile(1, profile_data)
        ...         assert profile.learning_progress.progress_data == "Chapter 2"
        ...         assert profile.preferences.preferences_data == "Light Mode"
        ...         print("Update test passed!")
        >>> asyncio.run(test_update_profile())
        Update test passed!
        """
        profile = await self.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Update learning_progress
        if profile_data.learning_progress:
            if profile.learning_progress:
                profile.learning_progress.progress_data = profile_data.learning_progress.progress_data
                profile.learning_progress.last_updated = datetime.utcnow()
            else:
                learning_progress = LearningProgress(
                    progress_data=profile_data.learning_progress.progress_data,
                    profile=profile
                )
                profile.learning_progress = learning_progress

        # Update preferences
        if profile_data.preferences:
            if profile.preferences:
                profile.preferences.preferences_data = profile_data.preferences.preferences_data
                profile.preferences.last_updated = datetime.utcnow()
            else:
                preferences = UserPreferences(
                    preferences_data=profile_data.preferences.preferences_data,
                    profile=profile
                )
                profile.preferences = preferences

        try:
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating profile: {e}")
            raise HTTPException(status_code=500, detail="Could not update profile")

        await self.db_session.refresh(profile)
        return profile

    async def delete_profile(self, user_id: int) -> None:
        """
        Delete a profile by user_id.

        Args:
            user_id (int): User ID.

        Raises:
            HTTPException: If profile not found or deletion fails.

        Doctest:
        >>> import asyncio
        >>> async def test_delete_profile():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         await repo.delete_profile(1)
        ...         profile = await repo.get_profile(1)
        ...         assert profile is None
        ...         print("Delete test passed!")
        >>> asyncio.run(test_delete_profile())
        Delete test passed!
        """
        profile = await self.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        await self.db_session.delete(profile)
        try:
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting profile: {e}")
            raise HTTPException(status_code=500, detail="Could not delete profile")


# Dependency for database session
async def get_db_session() -> AsyncSession:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session.
    """
    async with async_session() as session:
        yield session


# FastAPI application instance
app = FastAPI()


# API endpoints
@app.get("/profiles/{user_id}", response_model=ProfileMemorySchema)
async def read_profile(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a user profile by user ID.

    Args:
        user_id (int): User ID.
        db (AsyncSession): Database session.

    Returns:
        ProfileMemorySchema: User profile data.

    Raises:
        HTTPException: If profile not found.
    """
    repository = ProfileMemoryRepository(db)
    profile = await repository.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.post("/profiles", response_model=ProfileMemorySchema)
async def create_profile(profile_data: ProfileMemoryCreateSchema, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new user profile.

    Args:
        profile_data (ProfileMemoryCreateSchema): Profile data.
        db (AsyncSession): Database session.

    Returns:
        ProfileMemorySchema: Created profile data.

    Raises:
        HTTPException: If profile creation fails.
    """
    repository = ProfileMemoryRepository(db)
    profile = await repository.create_profile(profile_data)
    return profile


@app.put("/profiles/{user_id}", response_model=ProfileMemorySchema)
async def update_profile(user_id: int, profile_data: ProfileMemoryCreateSchema, db: AsyncSession = Depends(get_db_session)):
    """
    Update an existing user profile.

    Args:
        user_id (int): User ID.
        profile_data (ProfileMemoryCreateSchema): New profile data.
        db (AsyncSession): Database session.

    Returns:
        ProfileMemorySchema: Updated profile data.

    Raises:
        HTTPException: If profile not found or update fails.
    """
    repository = ProfileMemoryRepository(db)
    profile = await repository.update_profile(user_id, profile_data)
    return profile


@app.delete("/profiles/{user_id}")
async def delete_profile(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete a user profile.

    Args:
        user_id (int): User ID.
        db (AsyncSession): Database session.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If profile not found or deletion fails.
    """
    repository = ProfileMemoryRepository(db)
    await repository.delete_profile(user_id)
    return {"message": "Profile deleted successfully"}


# Initialize the database (create tables)
async def init_db():
    """
    Initialize the database by creating all tables.

    Usage:
    >>> import asyncio
    >>> asyncio.run(init_db())
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Run initialization if executed directly
if __name__ == "__main__":
    import uvicorn

    # Create tables
    asyncio.run(init_db())

    # Run the application
    uvicorn.run("profile_memory:app", host="127.0.0.1", port=8000, reload=True)