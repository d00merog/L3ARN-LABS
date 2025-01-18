"""
This module provides models and asynchronous CRUD operations for user profile storage,
learning progress, and user preferences.

Features:
- User profile storage
- Learning progress tracking
- User preferences management

Models:
- ProfileMemory
- LearningProgress
- UserPreferences
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    select,
    func,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import IntegrityError

from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Asynchronous Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


# SQLAlchemy ORM models

class ProfileMemory(Base):
    """
    SQLAlchemy ORM model for storing user profile information.

    Attributes:
        id (int): Primary key.
        user_id (str): Unique identifier for the user.
        created_at (datetime): Timestamp when the profile was created.
        updated_at (datetime): Timestamp when the profile was last updated.
        learning_progress (LearningProgress): Relationship to the user's learning progress.
        user_preferences (UserPreferences): Relationship to the user's preferences.
    """
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    learning_progress = relationship(
        "LearningProgress", back_populates="profile", uselist=False
    )
    user_preferences = relationship(
        "UserPreferences", back_populates="profile", uselist=False
    )


class LearningProgress(Base):
    """
    SQLAlchemy ORM model for storing user's learning progress.

    Attributes:
        id (int): Primary key.
        profile_id (int): Foreign key to the user's profile.
        progress_data (str): JSON serialized data of learning progress.
        last_updated (datetime): Timestamp when the progress was last updated.
    """
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), unique=True)
    progress_data = Column(String, nullable=False)
    last_updated = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile = relationship(
        "ProfileMemory", back_populates="learning_progress"
    )


class UserPreferences(Base):
    """
    SQLAlchemy ORM model for storing user's preferences.

    Attributes:
        id (int): Primary key.
        profile_id (int): Foreign key to the user's profile.
        preferences_data (str): JSON serialized data of user preferences.
        last_updated (datetime): Timestamp when the preferences were last updated.
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), unique=True)
    preferences_data = Column(String, nullable=False)
    last_updated = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile = relationship(
        "ProfileMemory", back_populates="user_preferences"
    )


# Pydantic models for validation

class ProfileMemoryBase(BaseModel):
    user_id: str = Field(..., example="user123")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('user_id')
    def user_id_must_not_be_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('user_id must not be empty')
        return v


class ProfileMemoryCreate(ProfileMemoryBase):
    pass


class ProfileMemoryUpdate(ProfileMemoryBase):
    pass


class ProfileMemoryInDBBase(ProfileMemoryBase):
    id: int

    class Config:
        orm_mode = True


class ProfileMemoryWithRelations(ProfileMemoryInDBBase):
    learning_progress: Optional['LearningProgress'] = None
    user_preferences: Optional['UserPreferences'] = None


class LearningProgressBase(BaseModel):
    progress_data: str = Field(..., example='{"lesson": "1", "score": "95"}')
    last_updated: Optional[datetime] = None

    @validator('progress_data')
    def progress_data_must_not_be_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('progress_data must not be empty')
        return v


class LearningProgressCreate(LearningProgressBase):
    pass


class LearningProgressUpdate(LearningProgressBase):
    pass


class LearningProgressInDBBase(LearningProgressBase):
    id: int
    profile_id: int

    class Config:
        orm_mode = True


class UserPreferencesBase(BaseModel):
    preferences_data: str = Field(..., example='{"theme": "dark"}')
    last_updated: Optional[datetime] = None

    @validator('preferences_data')
    def preferences_data_must_not_be_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('preferences_data must not be empty')
        return v


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferencesUpdate(UserPreferencesBase):
    pass


class UserPreferencesInDBBase(UserPreferencesBase):
    id: int
    profile_id: int

    class Config:
        orm_mode = True


# Asynchronous CRUD operations

async def create_profile_memory(
    db: AsyncSession, profile: ProfileMemoryCreate
) -> ProfileMemory:
    """
    Create a new ProfileMemory entry in the database.

    Args:
        db (AsyncSession): The database session.
        profile (ProfileMemoryCreate): The profile data to create.

    Returns:
        ProfileMemory: The created ProfileMemory instance.

    Raises:
        ValueError: If user_id already exists.

    Example:
        >>> import asyncio
        >>> async def test_create_profile():
        ...     async with async_session() as db:
        ...         new_profile = await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         assert new_profile.user_id == 'test_user'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_create_profile())
    """
    async with db.begin():
        existing_profile = await db.execute(
            select(func.count(ProfileMemory.id)).filter_by(user_id=profile.user_id)
        )
        (count,) = existing_profile.scalar_one()
        if count > 0:
            logger.error(f"User ID {profile.user_id} already exists.")
            raise ValueError("User ID already exists.")

        db_profile = ProfileMemory(user_id=profile.user_id)
        db.add(db_profile)
    await db.refresh(db_profile)
    logger.info(f"Created ProfileMemory for user_id {profile.user_id}.")
    return db_profile


async def get_profile_memory(
    db: AsyncSession, user_id: str
) -> Optional[ProfileMemory]:
    """
    Retrieve a ProfileMemory entry from the database by user_id.

    Args:
        db (AsyncSession): The database session.
        user_id (str): The user's unique identifier.

    Returns:
        Optional[ProfileMemory]: The retrieved ProfileMemory or None if not found.

    Example:
        >>> import asyncio
        >>> async def test_get_profile():
        ...     async with async_session() as db:
        ...         profile = await get_profile_memory(db, 'nonexistent_user')
        ...         assert profile is None
        ...         new_profile = await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         profile = await get_profile_memory(db, 'test_user')
        ...         assert profile.user_id == 'test_user'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_get_profile())
    """
    result = await db.execute(
        select(ProfileMemory).filter_by(user_id=user_id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        logger.info(f"Retrieved ProfileMemory for user_id {user_id}.")
    else:
        logger.warning(f"ProfileMemory not found for user_id {user_id}.")
    return profile


async def update_profile_memory(
    db: AsyncSession, user_id: str, profile_update: ProfileMemoryUpdate
) -> ProfileMemory:
    """
    Update an existing ProfileMemory entry.

    Args:
        db (AsyncSession): The database session.
        user_id (str): The user's unique identifier.
        profile_update (ProfileMemoryUpdate): The updated profile data.

    Returns:
        ProfileMemory: The updated ProfileMemory instance.

    Raises:
        ValueError: If ProfileMemory is not found.

    Example:
        >>> import asyncio
        >>> async def test_update_profile():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         updated_profile = await update_profile_memory(db, 'test_user', ProfileMemoryUpdate(user_id='test_user'))
        ...         assert updated_profile.user_id == 'test_user'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_update_profile())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile:
        logger.error(f"ProfileMemory not found for user_id {user_id}.")
        raise ValueError("ProfileMemory not found.")

    update_data = profile_update.dict(exclude_unset=True)
    for var, value in update_data.items():
        setattr(profile, var, value)

    async with db.begin():
        db.add(profile)
    await db.refresh(profile)
    logger.info(f"Updated ProfileMemory for user_id {user_id}.")
    return profile


async def delete_profile_memory(db: AsyncSession, user_id: str) -> None:
    """
    Delete a ProfileMemory entry from the database.

    Args:
        db (AsyncSession): The database session.
        user_id (str): The user's unique identifier.

    Raises:
        ValueError: If ProfileMemory is not found.

    Example:
        >>> import asyncio
        >>> async def test_delete_profile():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         await delete_profile_memory(db, 'test_user')
        ...         profile = await get_profile_memory(db, 'test_user')
        ...         assert profile is None
        >>> asyncio.run(test_delete_profile())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile:
        logger.error(f"ProfileMemory not found for user_id {user_id}.")
        raise ValueError("ProfileMemory not found.")

    async with db.begin():
        await db.delete(profile)
    logger.info(f"Deleted ProfileMemory for user_id {user_id}.")


async def create_or_update_learning_progress(
    db: AsyncSession, user_id: str, progress: LearningProgressCreate
) -> LearningProgress:
    """
    Create or update the LearningProgress for a given user.

    Args:
        db (AsyncSession): The database session.
        user_id (str): The user's unique identifier.
        progress (LearningProgressCreate): The learning progress data.

    Returns:
        LearningProgress: The created or updated LearningProgress instance.

    Raises:
        ValueError: If ProfileMemory is not found.

    Example:
        >>> import asyncio
        >>> async def test_learning_progress():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         lp = await create_or_update_learning_progress(
        ...             db,
        ...             'test_user',
        ...             LearningProgressCreate(progress_data='{"lesson": "2"}')
        ...         )
        ...         assert lp.progress_data == '{"lesson": "2"}'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_learning_progress())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile:
        logger.error(f"ProfileMemory not found for user_id {user_id}.")
        raise ValueError("ProfileMemory not found.")

    learning_progress = profile.learning_progress
    if not learning_progress:
        learning_progress = LearningProgress(
            progress_data=progress.progress_data, profile=profile
        )
    else:
        learning_progress.progress_data = progress.progress_data
        learning_progress.last_updated = datetime.utcnow()

    async with db.begin():
        db.add(learning_progress)
    await db.refresh(learning_progress)
    logger.info(f"Created/Updated LearningProgress for user_id {user_id}.")
    return learning_progress


async def get_learning_progress(
    db: AsyncSession, user_id: str
) -> Optional[LearningProgress]:
    """
    Retrieve the LearningProgress for a given user.

    Args:
        db (AsyncSession): The database session.
        user_id: The user's unique identifier.

    Returns:
        Optional[LearningProgress]: The LearningProgress entry or None if not found.

    Example:
        >>> import asyncio
        >>> async def test_get_learning_progress():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         progress = await get_learning_progress(db, 'test_user')
        ...         assert progress is None
        ...         await create_or_update_learning_progress(
        ...             db,
        ...             'test_user',
        ...             LearningProgressCreate(progress_data='{"lesson": "1"}')
        ...         )
        ...         progress = await get_learning_progress(db, 'test_user')
        ...         assert progress.progress_data == '{"lesson": "1"}'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_get_learning_progress())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile or not profile.learning_progress:
        logger.warning(f"LearningProgress not found for user_id {user_id}.")
        return None
    logger.info(f"Retrieved LearningProgress for user_id {user_id}.")
    return profile.learning_progress


async def create_or_update_user_preferences(
    db: AsyncSession, user_id: str, preferences: UserPreferencesCreate
) -> UserPreferences:
    """
    Create or update the UserPreferences for a given user.

    Args:
        db (AsyncSession): The database session.
        user_id (str): The user's unique identifier.
        preferences (UserPreferencesCreate): The user preferences data.

    Returns:
        UserPreferences: The created or updated UserPreferences instance.

    Raises:
        ValueError: If ProfileMemory is not found.

    Example:
        >>> import asyncio
        >>> async def test_user_preferences():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         prefs = await create_or_update_user_preferences(
        ...             db,
        ...             'test_user',
        ...             UserPreferencesCreate(preferences_data='{"theme": "light"}')
        ...         )
        ...         assert prefs.preferences_data == '{"theme": "light"}'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_user_preferences())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile:
        logger.error(f"ProfileMemory not found for user_id {user_id}.")
        raise ValueError("ProfileMemory not found.")

    user_preferences = profile.user_preferences
    if not user_preferences:
        user_preferences = UserPreferences(
            preferences_data=preferences.preferences_data, profile=profile
        )
    else:
        user_preferences.preferences_data = preferences.preferences_data
        user_preferences.last_updated = datetime.utcnow()

    async with db.begin():
        db.add(user_preferences)
    await db.refresh(user_preferences)
    logger.info(f"Created/Updated UserPreferences for user_id {user_id}.")
    return user_preferences


async def get_user_preferences(
    db: AsyncSession, user_id: str
) -> Optional[UserPreferences]:
    """
    Retrieve the UserPreferences for a given user.

    Args:
        db (AsyncSession): The database session.
        user_id: The user's unique identifier.

    Returns:
        Optional[UserPreferences]: The UserPreferences entry or None if not found.

    Example:
        >>> import asyncio
        >>> async def test_get_user_preferences():
        ...     async with async_session() as db:
        ...         await create_profile_memory(db, ProfileMemoryCreate(user_id='test_user'))
        ...         prefs = await get_user_preferences(db, 'test_user')
        ...         assert prefs is None
        ...         await create_or_update_user_preferences(
        ...             db,
        ...             'test_user',
        ...             UserPreferencesCreate(preferences_data='{"notifications": "on"}')
        ...         )
        ...         prefs = await get_user_preferences(db, 'test_user')
        ...         assert prefs.preferences_data == '{"notifications": "on"}'
        ...         await delete_profile_memory(db, 'test_user')
        >>> asyncio.run(test_get_user_preferences())
    """
    profile = await get_profile_memory(db, user_id)
    if not profile or not profile.user_preferences:
        logger.warning(f"UserPreferences not found for user_id {user_id}.")
        return None
    logger.info(f"Retrieved UserPreferences for user_id {user_id}.")
    return profile.user_preferences


# Create database tables (for demonstration purposes)

async def init_db():
    """
    Initialize the database by creating all tables.

    Example:
        >>> import asyncio
        >>> asyncio.run(init_db())
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")


# Ensure that the forward references are resolved
ProfileMemoryWithRelations.update_forward_refs()