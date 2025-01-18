"""
profile_memory.py

This module provides the backend functionality for managing user profile storage,
learning progress, and user preferences. It includes models, schemas, services,
and API routes following best practices.

Features:
- User profile storage
- Learning progress tracking
- User preferences management

Models:
- ProfileMemory
- LearningProgress
- UserPreferences

Architecture:
- Repository pattern
- Dependency injection
- Async operations

Dependencies:
- FastAPI
- SQLAlchemy (Async)
- Pydantic
- Asyncio
- Typing
- Datetime

Usage:
Run this module with an ASGI server (e.g., Uvicorn) to start the API service.
"""

from typing import List, Optional
import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    select,
)
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


# Database Models
class ProfileMemory(Base):
    """
    SQLAlchemy model for ProfileMemory.

    Represents user's profile memory, including relationships to learning progress
    and user preferences.
    """

    __tablename__ = "profile_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    learning_progress = relationship(
        "LearningProgress", back_populates="profile_memory", uselist=False
    )
    user_preferences = relationship(
        "UserPreferences", back_populates="profile_memory", uselist=False
    )

    def __repr__(self):
        return f"<ProfileMemory(user_id={self.user_id})>"


class LearningProgress(Base):
    """
    SQLAlchemy model for LearningProgress.

    Stores the learning progress data associated with a profile memory.
    """

    __tablename__ = "learning_progresses"

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey("profile_memories.id"), unique=True)
    progress_data = Column(String, nullable=False)

    profile_memory = relationship("ProfileMemory", back_populates="learning_progress")

    def __repr__(self):
        return f"<LearningProgress(profile_memory_id={self.profile_memory_id})>"


class UserPreferences(Base):
    """
    SQLAlchemy model for UserPreferences.

    Stores the user preferences data associated with a profile memory.
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey("profile_memories.id"), unique=True)
    preferences_data = Column(String, nullable=False)

    profile_memory = relationship("ProfileMemory", back_populates="user_preferences")

    def __repr__(self):
        return f"<UserPreferences(profile_memory_id={self.profile_memory_id})>"


# Pydantic Schemas
class LearningProgressBase(BaseModel):
    """
    Base schema for LearningProgress.
    """

    progress_data: str = Field(..., max_length=500)


class LearningProgressCreate(LearningProgressBase):
    """
    Schema for creating LearningProgress.
    """

    pass


class LearningProgressUpdate(LearningProgressBase):
    """
    Schema for updating LearningProgress.
    """

    pass


class LearningProgressInDB(LearningProgressBase):
    """
    Schema representing LearningProgress in the database.
    """

    id: int
    profile_memory_id: int

    class Config:
        orm_mode = True


class UserPreferencesBase(BaseModel):
    """
    Base schema for UserPreferences.
    """

    preferences_data: str = Field(..., max_length=500)


class UserPreferencesCreate(UserPreferencesBase):
    """
    Schema for creating UserPreferences.
    """

    pass


class UserPreferencesUpdate(UserPreferencesBase):
    """
    Schema for updating UserPreferences.
    """

    pass


class UserPreferencesInDB(UserPreferencesBase):
    """
    Schema representing UserPreferences in the database.
    """

    id: int
    profile_memory_id: int

    class Config:
        orm_mode = True


class ProfileMemoryBase(BaseModel):
    """
    Base schema for ProfileMemory.
    """

    user_id: int


class ProfileMemoryCreate(ProfileMemoryBase):
    """
    Schema for creating ProfileMemory.
    """

    learning_progress: Optional[LearningProgressCreate] = None
    user_preferences: Optional[UserPreferencesCreate] = None


class ProfileMemoryUpdate(ProfileMemoryBase):
    """
    Schema for updating ProfileMemory.
    """

    learning_progress: Optional[LearningProgressUpdate] = None
    user_preferences: Optional[UserPreferencesUpdate] = None


class ProfileMemoryInDB(ProfileMemoryBase):
    """
    Schema representing ProfileMemory in the database.
    """

    id: int
    created_at: datetime
    updated_at: datetime
    learning_progress: Optional[LearningProgressInDB] = None
    user_preferences: Optional[UserPreferencesInDB] = None

    class Config:
        orm_mode = True


# Services
async def get_profile_memory(
    db: AsyncSession, user_id: int
) -> Optional[ProfileMemory]:
    """
    Retrieve a profile memory by user_id.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The user ID.

    Returns:
        Optional[ProfileMemory]: The profile memory if found, else None.

    Doctest:
    >>> async def test_get_profile_memory():
    ...     async with async_session() as db:
    ...         profile = await get_profile_memory(db, user_id=1)
    ...         assert profile is None
    >>> asyncio.run(test_get_profile_memory())
    """
    try:
        result = await db.execute(
            select(ProfileMemory).where(ProfileMemory.user_id == user_id)
        )
        profile_memory = result.scalar_one_or_none()
        return profile_memory
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving profile memory for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_profile_memory(
    db: AsyncSession, profile_data: ProfileMemoryCreate
) -> ProfileMemory:
    """
    Create a new profile memory.

    Args:
        db (AsyncSession): The database session.
        profile_data (ProfileMemoryCreate): The profile data.

    Returns:
        ProfileMemory: The created profile memory.

    Doctest:
    >>> async def test_create_profile_memory():
    ...     async with async_session() as db:
    ...         profile_data = ProfileMemoryCreate(
    ...             user_id=1,
    ...             learning_progress=LearningProgressCreate(progress_data="{}"),
    ...             user_preferences=UserPreferencesCreate(preferences_data="{}")
    ...         )
    ...         profile = await create_profile_memory(db, profile_data)
    ...         assert profile.id > 0
    ...         assert profile.user_id == 1
    >>> asyncio.run(test_create_profile_memory())
    """
    async with db.begin():
        try:
            profile_memory = ProfileMemory(user_id=profile_data.user_id)
            db.add(profile_memory)
            await db.flush()  # To get the profile_memory.id before inserting related data

            if profile_data.learning_progress:
                learning_progress = LearningProgress(
                    profile_memory_id=profile_memory.id,
                    progress_data=profile_data.learning_progress.progress_data,
                )
                db.add(learning_progress)

            if profile_data.user_preferences:
                user_preferences = UserPreferences(
                    profile_memory_id=profile_memory.id,
                    preferences_data=profile_data.user_preferences.preferences_data,
                )
                db.add(user_preferences)

            await db.commit()
            await db.refresh(profile_memory)
            logger.info(f"Created ProfileMemory for user_id {profile_data.user_id}")
            return profile_memory
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating profile memory: {e}")
            raise HTTPException(status_code=400, detail="Error creating profile memory")


async def update_profile_memory(
    db: AsyncSession, profile_memory: ProfileMemory, profile_update: ProfileMemoryUpdate
) -> ProfileMemory:
    """
    Update an existing profile memory.

    Args:
        db (AsyncSession): The database session.
        profile_memory (ProfileMemory): The profile memory to update.
        profile_update (ProfileMemoryUpdate): The updated profile data.

    Returns:
        ProfileMemory: The updated profile memory.

    Doctest:
    >>> async def test_update_profile_memory():
    ...     async with async_session() as db:
    ...         # Assume profile_memory with user_id=1 exists
    ...         profile_memory = await get_profile_memory(db, user_id=1)
    ...         profile_update = ProfileMemoryUpdate(
    ...             user_id=1,
    ...             learning_progress=LearningProgressUpdate(progress_data='{"progress": 50}'),
    ...             user_preferences=UserPreferencesUpdate(preferences_data='{"theme": "dark"}')
    ...         )
    ...         updated_profile = await update_profile_memory(db, profile_memory, profile_update)
    ...         assert updated_profile.learning_progress.progress_data == '{"progress": 50}'
    ...         assert updated_profile.user_preferences.preferences_data == '{"theme": "dark"}'
    >>> asyncio.run(test_update_profile_memory())
    """
    async with db.begin():
        try:
            if profile_update.user_id:
                profile_memory.user_id = profile_update.user_id

            profile_memory.updated_at = datetime.utcnow()

            if profile_update.learning_progress:
                if profile_memory.learning_progress:
                    profile_memory.learning_progress.progress_data = profile_update.learning_progress.progress_data
                else:
                    learning_progress = LearningProgress(
                        profile_memory_id=profile_memory.id,
                        progress_data=profile_update.learning_progress.progress_data,
                    )
                    db.add(learning_progress)

            if profile_update.user_preferences:
                if profile_memory.user_preferences:
                    profile_memory.user_preferences.preferences_data = profile_update.user_preferences.preferences_data
                else:
                    user_preferences = UserPreferences(
                        profile_memory_id=profile_memory.id,
                        preferences_data=profile_update.user_preferences.preferences_data,
                    )
                    db.add(user_preferences)

            await db.commit()
            await db.refresh(profile_memory)
            logger.info(f"Updated ProfileMemory for user_id {profile_memory.user_id}")
            return profile_memory
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating profile memory: {e}")
            raise HTTPException(status_code=400, detail="Error updating profile memory")


async def delete_profile_memory(db: AsyncSession, profile_memory: ProfileMemory):
    """
    Delete a profile memory.

    Args:
        db (AsyncSession): The database session.
        profile_memory (ProfileMemory): The profile memory to delete.

    Returns:
        None

    Doctest:
    >>> async def test_delete_profile_memory():
    ...     async with async_session() as db:
    ...         profile_memory = await get_profile_memory(db, user_id=1)
    ...         if profile_memory:
    ...             await delete_profile_memory(db, profile_memory)
    ...             profile_memory = await get_profile_memory(db, user_id=1)
    ...             assert profile_memory is None
    >>> asyncio.run(test_delete_profile_memory())
    """
    async with db.begin():
        try:
            await db.delete(profile_memory)
            await db.commit()
            logger.info(f"Deleted ProfileMemory for user_id {profile_memory.user_id}")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting profile memory: {e}")
            raise HTTPException(status_code=400, detail="Error deleting profile memory")


# Dependency Injection
async def get_db() -> AsyncSession:
    """
    Dependency to get an async database session.
    """
    async with async_session() as session:
        yield session


# FastAPI Application and Routes
app = FastAPI(title="Profile Memory Service", version="1.0.0")
router = APIRouter()


@router.post(
    "/profile_memory/",
    response_model=ProfileMemoryInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new profile memory",
    tags=["ProfileMemory"],
)
async def create_profile(
    profile: ProfileMemoryCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new profile memory for a user.

    Args:
        profile (ProfileMemoryCreate): The profile data.
        db (AsyncSession): The database session.

    Returns:
        ProfileMemoryInDB: The created profile memory.
    """
    existing_profile = await get_profile_memory(db, profile.user_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile_memory = await create_profile_memory(db, profile)
    return profile_memory


@router.get(
    "/profile_memory/{user_id}",
    response_model=ProfileMemoryInDB,
    summary="Retrieve a profile memory",
    tags=["ProfileMemory"],
)
async def read_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a profile memory by user ID.

    Args:
        user_id (int): The user ID.
        db (AsyncSession): The database session.

    Returns:
        ProfileMemoryInDB: The retrieved profile memory.
    """
    profile_memory = await get_profile_memory(db, user_id)
    if not profile_memory:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_memory


@router.put(
    "/profile_memory/{user_id}",
    response_model=ProfileMemoryInDB,
    summary="Update a profile memory",
    tags=["ProfileMemory"],
)
async def update_profile(
    user_id: int, profile_update: ProfileMemoryUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing profile memory by user ID.

    Args:
        user_id (int): The user ID.
        profile_update (ProfileMemoryUpdate): The updated profile data.
        db (AsyncSession): The database session.

    Returns:
        ProfileMemoryInDB: The updated profile memory.
    """
    profile_memory = await get_profile_memory(db, user_id)
    if not profile_memory:
        raise HTTPException(status_code=404, detail="Profile not found")
    updated_profile = await update_profile_memory(db, profile_memory, profile_update)
    return updated_profile


@router.delete(
    "/profile_memory/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a profile memory",
    tags=["ProfileMemory"],
)
async def delete_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a profile memory by user ID.

    Args:
        user_id (int): The user ID.
        db (AsyncSession): The database session.

    Returns:
        None
    """
    profile_memory = await get_profile_memory(db, user_id)
    if not profile_memory:
        raise HTTPException(status_code=404, detail="Profile not found")
    await delete_profile_memory(db, profile_memory)
    return None


app.include_router(router)


# Event Handlers
@app.on_event("startup")
async def startup():
    """
    Event handler for startup.

    Initializes the database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


@app.on_event("shutdown")
async def shutdown():
    """
    Event handler for shutdown.

    Disposes the database engine.
    """
    await engine.dispose()
    logger.info("Database connection closed")


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("profile_memory:app", host="0.0.0.0", port=8000, reload=True)