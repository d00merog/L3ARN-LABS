"""
Profile Memory module.

This module provides classes and functions to manage user profiles, learning progress, and user preferences.

Features:
- User profile storage
- Learning progress tracking
- Preferences management

Usage:
    python profile_memory.py

Unit tests are included as doctests in the docstrings.

"""

import logging
import asyncio
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from pydantic import BaseModel, validator, ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Using SQLite for demonstration purposes

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


# Data models
class ProfileMemory(Base):
    """
    SQLAlchemy model for storing user profiles.

    Attributes:
        id (int): Primary key
        name (str): User's name
        created_at (datetime): Account creation timestamp
        learning_progress (List[LearningProgress]): Relationship to learning progress
        preferences (UserPreferences): One-to-one relationship to user preferences

    Doctest:
        >>> asyncio.run(test_profile_memory())
    """
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # relationships
    learning_progress = relationship('LearningProgress', back_populates='profile', cascade="all, delete-orphan")
    preferences = relationship('UserPreferences', uselist=False, back_populates='profile', cascade="all, delete-orphan")


class LearningProgress(Base):
    """
    SQLAlchemy model for tracking learning progress.

    Attributes:
        id (int): Primary key
        profile_id (int): Foreign key to ProfileMemory
        course_name (str): Name of the course
        progress (int): Progress percentage
        updated_at (datetime): Last updated timestamp
        profile (ProfileMemory): Relationship back to profile

    Doctest:
        >>> asyncio.run(test_learning_progress())
    """
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'))
    course_name = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    # relationships
    profile = relationship('ProfileMemory', back_populates='learning_progress')


class UserPreferences(Base):
    """
    SQLAlchemy model for storing user preferences.

    Attributes:
        id (int): Primary key
        profile_id (int): Foreign key to ProfileMemory
        preferences (str): JSON string of preferences
        profile (ProfileMemory): Relationship back to profile

    Doctest:
        >>> asyncio.run(test_user_preferences())
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'))
    preferences = Column(Text, nullable=False)
    # relationships
    profile = relationship('ProfileMemory', back_populates='preferences')


# Pydantic models for validation
class ProfileMemoryCreate(BaseModel):
    name: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name must not be empty')
        return v


class LearningProgressCreate(BaseModel):
    profile_id: int
    course_name: str
    progress: int

    @validator('progress')
    def progress_must_be_between_0_and_100(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Progress must be between 0 and 100')
        return v

    @validator('course_name')
    def course_name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Course name must not be empty')
        return v


class UserPreferencesCreate(BaseModel):
    profile_id: int
    preferences: str

    @validator('preferences')
    def preferences_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Preferences must not be empty')
        return v


# CRUD operations using async functions
class ProfileMemoryService:
    """
    Service class for ProfileMemory operations.

    Doctest:
        >>> asyncio.run(test_profile_memory_service())
    """

    @staticmethod
    async def create_profile(session: AsyncSession, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new user profile.

        Args:
            session (AsyncSession): The database session.
            profile_data (ProfileMemoryCreate): The data for the new profile.

        Returns:
            ProfileMemory: The created profile.

        Raises:
            ValidationError: If input validation fails.
        """
        try:
            profile_data = ProfileMemoryCreate(**profile_data.dict())
            new_profile = ProfileMemory(name=profile_data.name)
            session.add(new_profile)
            await session.commit()
            await session.refresh(new_profile)
            logger.info(f"Created new profile with ID {new_profile.id}")
            return new_profile
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise

    @staticmethod
    async def get_profile(session: AsyncSession, profile_id: int) -> Optional[ProfileMemory]:
        """
        Get a user profile by ID.

        Args:
            session (AsyncSession): The database session.
            profile_id (int): The ID of the profile.

        Returns:
            Optional[ProfileMemory]: The profile if found, else None.
        """
        result = await session.get(ProfileMemory, profile_id)
        if result is None:
            logger.warning(f"Profile with ID {profile_id} not found")
        else:
            logger.info(f"Retrieved profile with ID {profile_id}")
        return result

    @staticmethod
    async def delete_profile(session: AsyncSession, profile_id: int) -> bool:
        """
        Delete a user profile by ID.

        Args:
            session (AsyncSession): The database session.
            profile_id (int): The ID of the profile.

        Returns:
            bool: True if deleted, False otherwise.
        """
        profile = await ProfileMemoryService.get_profile(session, profile_id)
        if profile:
            await session.delete(profile)
            await session.commit()
            logger.info(f"Deleted profile with ID {profile_id}")
            return True
        logger.warning(f"Cannot delete, profile with ID {profile_id} does not exist")
        return False


class LearningProgressService:
    """
    Service class for LearningProgress operations.

    Doctest:
        >>> asyncio.run(test_learning_progress_service())
    """

    @staticmethod
    async def add_progress(session: AsyncSession, progress_data: LearningProgressCreate) -> LearningProgress:
        """
        Add learning progress for a profile.

        Args:
            session (AsyncSession): The database session.
            progress_data (LearningProgressCreate): The progress data.

        Returns:
            LearningProgress: The created learning progress entry.

        Raises:
            ValidationError: If input validation fails.
        """
        try:
            progress_data = LearningProgressCreate(**progress_data.dict())
            new_progress = LearningProgress(
                profile_id=progress_data.profile_id,
                course_name=progress_data.course_name,
                progress=progress_data.progress
            )
            session.add(new_progress)
            await session.commit()
            await session.refresh(new_progress)
            logger.info(f"Added learning progress ID {new_progress.id} for profile ID {new_progress.profile_id}")
            return new_progress
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise

    @staticmethod
    async def get_progress_by_profile(session: AsyncSession, profile_id: int) -> List[LearningProgress]:
        """
        Get all learning progress entries for a profile.

        Args:
            session (AsyncSession): The database session.
            profile_id (int): The profile ID.

        Returns:
            List[LearningProgress]: List of learning progress entries.
        """
        result = await session.execute(
            learning_progress_table.select().where(LearningProgress.profile_id == profile_id)
        )
        progress_list = result.scalars().all()
        logger.info(f"Retrieved {len(progress_list)} progress entries for profile ID {profile_id}")
        return progress_list


class UserPreferencesService:
    """
    Service class for UserPreferences operations.

    Doctest:
        >>> asyncio.run(test_user_preferences_service())
    """

    @staticmethod
    async def set_preferences(session: AsyncSession, preferences_data: UserPreferencesCreate) -> UserPreferences:
        """
        Set preferences for a profile.

        Args:
            session (AsyncSession): The database session.
            preferences_data (UserPreferencesCreate): The preferences data.

        Returns:
            UserPreferences: The created or updated user preferences entry.

        Raises:
            ValidationError: If input validation fails.
        """
        try:
            preferences_data = UserPreferencesCreate(**preferences_data.dict())

            # Check if preferences already exist
            result = await session.execute(
                user_preferences_table.select().where(UserPreferences.profile_id == preferences_data.profile_id)
            )
            existing_preferences = result.scalar_one_or_none()

            if existing_preferences:
                existing_preferences.preferences = preferences_data.preferences
                await session.commit()
                await session.refresh(existing_preferences)
                logger.info(f"Updated preferences for profile ID {existing_preferences.profile_id}")
                return existing_preferences
            else:
                new_preferences = UserPreferences(
                    profile_id=preferences_data.profile_id,
                    preferences=preferences_data.preferences
                )
                session.add(new_preferences)
                await session.commit()
                await session.refresh(new_preferences)
                logger.info(f"Set new preferences for profile ID {new_preferences.profile_id}")
                return new_preferences
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise

    @staticmethod
    async def get_preferences(session: AsyncSession, profile_id: int) -> Optional[UserPreferences]:
        """
        Get preferences for a profile.

        Args:
            session (AsyncSession): The database session.
            profile_id (int): The profile ID.

        Returns:
            Optional[UserPreferences]: The user preferences if found, else None.
        """
        result = await session.execute(
            user_preferences_table.select().where(UserPreferences.profile_id == profile_id)
        )
        preferences = result.scalar_one_or_none()
        if preferences:
            logger.info(f"Retrieved preferences for profile ID {profile_id}")
        else:
            logger.warning(f"No preferences found for profile ID {profile_id}")
        return preferences

# Aliases for table objects (for query building)
profile_memory_table = ProfileMemory.__table__
learning_progress_table = LearningProgress.__table__
user_preferences_table = UserPreferences.__table__


# Testing functions using doctest
async def test_profile_memory():
    """
    Test creating and retrieving a profile.

    Doctest:
        >>> asyncio.run(test_profile_memory())
    """
    async with async_session() as session:
        # Create
        profile_data = ProfileMemoryCreate(name="Alice")
        profile = await ProfileMemoryService.create_profile(session, profile_data)
        assert profile.name == "Alice"

        # Retrieve
        retrieved_profile = await ProfileMemoryService.get_profile(session, profile.id)
        assert retrieved_profile.id == profile.id
        assert retrieved_profile.name == "Alice"

async def test_learning_progress():
    """
    Test adding learning progress.

    Doctest:
        >>> asyncio.run(test_learning_progress())
    """
    async with async_session() as session:
        # First, create a profile
        profile_data = ProfileMemoryCreate(name="Bob")
        profile = await ProfileMemoryService.create_profile(session, profile_data)

        # Add progress
        progress_data = LearningProgressCreate(
            profile_id=profile.id,
            course_name="Python Basics",
            progress=50
        )
        progress = await LearningProgressService.add_progress(session, progress_data)
        assert progress.profile_id == profile.id
        assert progress.course_name == "Python Basics"
        assert progress.progress == 50

async def test_user_preferences():
    """
    Test setting user preferences.

    Doctest:
        >>> asyncio.run(test_user_preferences())
    """
    async with async_session() as session:
        # First, create a profile
        profile_data = ProfileMemoryCreate(name="Carol")
        profile = await ProfileMemoryService.create_profile(session, profile_data)

        # Set preferences
        preferences_data = UserPreferencesCreate(
            profile_id=profile.id,
            preferences='{"theme": "dark", "notifications": true}'
        )
        preferences = await UserPreferencesService.set_preferences(session, preferences_data)
        assert preferences.profile_id == profile.id
        assert preferences.preferences == '{"theme": "dark", "notifications": true}'

        # Get preferences
        retrieved_preferences = await UserPreferencesService.get_preferences(session, profile.id)
        assert retrieved_preferences.preferences == '{"theme": "dark", "notifications": true}'


async def test_profile_memory_service():
    """
    Test the ProfileMemoryService.

    Doctest:
        >>> asyncio.run(test_profile_memory_service())
    """
    await test_profile_memory()

async def test_learning_progress_service():
    """
    Test the LearningProgressService.

    Doctest:
        >>> asyncio.run(test_learning_progress_service())
    """
    await test_learning_progress()

async def test_user_preferences_service():
    """
    Test the UserPreferencesService.

    Doctest:
        >>> asyncio.run(test_user_preferences_service())
    """
    await test_user_preferences()


# Main execution
async def main():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run tests
    await test_profile_memory()
    await test_learning_progress()
    await test_user_preferences()
    logger.info("All tests passed.")


if __name__ == '__main__':
    asyncio.run(main())