"""
This module provides classes and functions to handle user profile storage,
learning progress tracking, and user preferences management using async
operations with SQLAlchemy and Pydantic for input validation.

Features:
- User profile storage
- Learning progress tracking
- User preferences management

Architecture patterns:
- Repository pattern
- Dependency injection
- Async operations
"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    create_engine,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

from pydantic import BaseModel, Field, validator, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base class for declarative class definitions
Base = declarative_base()


# SQLAlchemy models
class ProfileMemory(Base):
    """
    SQLAlchemy model for storing user profile information.

    Relationships:
    - learning_progresses: One-to-many with LearningProgress
    - preferences: One-to-one with UserPreferences
    """

    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    learning_progresses = relationship(
        'LearningProgress',
        back_populates='profile',
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        'UserPreferences',
        back_populates='profile',
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ProfileMemory(id={self.id}, user_id={self.user_id})>"


class LearningProgress(Base):
    """
    SQLAlchemy model for tracking user's learning progress.

    Relationships:
    - profile: Many-to-one with ProfileMemory
    """

    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), nullable=False)
    course_name = Column(String(255), nullable=False)
    progress_percentage = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    profile = relationship('ProfileMemory', back_populates='learning_progresses')

    def __repr__(self):
        return f"<LearningProgress(id={self.id}, course_name='{self.course_name}')>"


class UserPreferences(Base):
    """
    SQLAlchemy model for storing user preferences.

    Relationships:
    - profile: One-to-one with ProfileMemory
    """

    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile_memory.id'), nullable=False, unique=True)
    preferences_data = Column(Text)

    profile = relationship('ProfileMemory', back_populates='preferences')

    def __repr__(self):
        return f"<UserPreferences(id={self.id}, profile_id={self.profile_id})>"


# Pydantic models for input validation
class LearningProgressCreate(BaseModel):
    """
    Pydantic model for creating a LearningProgress instance.
    """

    course_name: str = Field(..., max_length=255)
    progress_percentage: int = Field(0, ge=0, le=100)

    @validator('course_name')
    def course_name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("course_name must not be empty")
        return v


class UserPreferencesCreate(BaseModel):
    """
    Pydantic model for creating a UserPreferences instance.
    """

    preferences_data: str = Field(...)

    @validator('preferences_data')
    def preferences_data_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("preferences_data must not be empty")
        return v


class ProfileMemoryCreate(BaseModel):
    """
    Pydantic model for creating a ProfileMemory instance.
    """

    user_id: int = Field(..., gt=0)
    preferences: Optional[UserPreferencesCreate]
    learning_progresses: Optional[List[LearningProgressCreate]] = []

    @validator('user_id')
    def user_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("user_id must be positive")
        return v


# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./profile_memory.db"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_db():
    """
    Initialize the database by creating all tables.

    This function should be run before any database operations are performed.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")


# Services
class ProfileService:
    """
    Service class for managing ProfileMemory operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new ProfileMemory record.

        :param profile_data: ProfileMemoryCreate Pydantic model
        :return: The created ProfileMemory instance

        >>> import asyncio
        >>> async def test():
        ...     await init_db()
        ...     async with AsyncSessionLocal() as session:
        ...         service = ProfileService(session)
        ...         profile_data = ProfileMemoryCreate(
        ...             user_id=1,
        ...             preferences=UserPreferencesCreate(preferences_data='{"theme": "dark"}'),
        ...             learning_progresses=[
        ...                 LearningProgressCreate(course_name="Math", progress_percentage=50),
        ...                 LearningProgressCreate(course_name="Science", progress_percentage=75)
        ...             ]
        ...         )
        ...         profile = await service.create_profile(profile_data)
        ...         assert profile.user_id == 1
        ...         assert profile.preferences.preferences_data == '{"theme": "dark"}'
        ...         assert len(profile.learning_progresses) == 2
        >>> asyncio.run(test())
        """
        try:
            new_profile = ProfileMemory(user_id=profile_data.user_id)

            if profile_data.preferences:
                new_preferences = UserPreferences(
                    preferences_data=profile_data.preferences.preferences_data
                )
                new_profile.preferences = new_preferences

            if profile_data.learning_progresses:
                for lp_data in profile_data.learning_progresses:
                    new_lp = LearningProgress(
                        course_name=lp_data.course_name,
                        progress_percentage=lp_data.progress_percentage,
                    )
                    new_profile.learning_progresses.append(new_lp)

            self.session.add(new_profile)
            await self.session.commit()
            await self.session.refresh(new_profile)
            logger.info(f"Created ProfileMemory with user_id {new_profile.user_id}")
            return new_profile
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating profile: {e}")
            raise

    async def get_profile(self, user_id: int) -> Optional[ProfileMemory]:
        """
        Retrieve a ProfileMemory by user_id.

        :param user_id: The user ID
        :return: The ProfileMemory instance or None

        >>> import asyncio
        >>> async def test():
        ...     await init_db()
        ...     async with AsyncSessionLocal() as session:
        ...         service = ProfileService(session)
        ...         profile = await service.get_profile(1)
        ...         assert profile is not None
        ...         assert profile.user_id == 1
        >>> asyncio.run(test())
        """
        try:
            result = await self.session.execute(
                select(ProfileMemory).where(ProfileMemory.user_id == user_id)
            )
            profile = result.scalars().first()
            logger.info(f"Retrieved ProfileMemory with user_id {user_id}")
            return profile
        except Exception as e:
            logger.error(f"Error retrieving profile: {e}")
            raise

    async def update_profile(
        self, user_id: int, update_data: ProfileMemoryCreate
    ) -> ProfileMemory:
        """
        Update an existing ProfileMemory record.

        :param user_id: The user ID to update
        :param update_data: The data to update
        :return: The updated ProfileMemory instance

        >>> import asyncio
        >>> async def test():
        ...     await init_db()
        ...     async with AsyncSessionLocal() as session:
        ...         service = ProfileService(session)
        ...         update_data = ProfileMemoryCreate(
        ...             user_id=1,
        ...             preferences=UserPreferencesCreate(preferences_data='{"theme": "light"}'),
        ...         )
        ...         profile = await service.update_profile(1, update_data)
        ...         assert profile.preferences.preferences_data == '{"theme": "light"}'
        >>> asyncio.run(test())
        """
        try:
            profile = await self.get_profile(user_id)
            if profile is None:
                raise ValueError(f"Profile with user_id {user_id} not found.")

            if update_data.preferences:
                if profile.preferences:
                    profile.preferences.preferences_data = update_data.preferences.preferences_data
                else:
                    new_preferences = UserPreferences(
                        preferences_data=update_data.preferences.preferences_data
                    )
                    profile.preferences = new_preferences

            if update_data.learning_progresses:
                # Remove existing learning progresses
                profile.learning_progresses.clear()
                for lp_data in update_data.learning_progresses:
                    new_lp = LearningProgress(
                        course_name=lp_data.course_name,
                        progress_percentage=lp_data.progress_percentage,
                    )
                    profile.learning_progresses.append(new_lp)

            await self.session.commit()
            await self.session.refresh(profile)
            logger.info(f"Updated ProfileMemory with user_id {user_id}")
            return profile
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating profile: {e}")
            raise

    async def delete_profile(self, user_id: int) -> None:
        """
        Delete a ProfileMemory by user_id.

        :param user_id: The user ID
        :return: None

        >>> import asyncio
        >>> async def test():
        ...     await init_db()
        ...     async with AsyncSessionLocal() as session:
        ...         service = ProfileService(session)
        ...         await service.delete_profile(1)
        ...         profile = await service.get_profile(1)
        ...         assert profile is None
        >>> asyncio.run(test())
        """
        try:
            profile = await self.get_profile(user_id)
            if profile is None:
                raise ValueError(f"Profile with user_id {user_id} not found.")
            await self.session.delete(profile)
            await self.session.commit()
            logger.info(f"Deleted ProfileMemory with user_id {user_id}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting profile: {e}")
            raise


# Example of how to use the service
async def main():
    """
    Main function to demonstrate the usage of ProfileService.
    """
    await init_db()
    async with AsyncSessionLocal() as session:
        service = ProfileService(session)

        # Create a new profile
        profile_data = ProfileMemoryCreate(
            user_id=1,
            preferences=UserPreferencesCreate(preferences_data='{"language": "en"}'),
            learning_progresses=[
                LearningProgressCreate(course_name="Math", progress_percentage=80),
                LearningProgressCreate(course_name="History", progress_percentage=60),
            ],
        )
        profile = await service.create_profile(profile_data)
        print(f"Created profile: {profile}")

        # Retrieve the profile
        retrieved_profile = await service.get_profile(1)
        print(f"Retrieved profile: {retrieved_profile}")

        # Update the profile
        update_data = ProfileMemoryCreate(
            user_id=1,
            preferences=UserPreferencesCreate(preferences_data='{"language": "es"}'),
            learning_progresses=[
                LearningProgressCreate(course_name="Science", progress_percentage=70)
            ],
        )
        updated_profile = await service.update_profile(1, update_data)
        print(f"Updated profile: {updated_profile}")

        # Delete the profile
        await service.delete_profile(1)
        print("Profile deleted.")


if __name__ == "__main__":
    asyncio.run(main())