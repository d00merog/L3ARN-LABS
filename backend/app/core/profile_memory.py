"""
Module: profile_memory.py

This module defines the data models and services for user profile memory,
learning progress, and user preferences. It includes asynchronous CRUD operations,
input validation, error handling, and logging.

Classes:
    - ProfileMemory: SQLAlchemy ORM model for user profile memory.
    - LearningProgress: SQLAlchemy ORM model for user learning progress.
    - UserPreferences: SQLAlchemy ORM model for user preferences.
    - ProfileMemoryService: Service class for ProfileMemory operations.
    - LearningProgressService: Service class for LearningProgress operations.
    - UserPreferencesService: Service class for UserPreferences operations.

Note:
    This module requires an async database session (AsyncSession) and is intended
    to be used within an asynchronous environment.
"""

import logging
import asyncio
from typing import Optional

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, declarative_base

from pydantic import BaseModel, validator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy base
Base = declarative_base()


# ORM Models
class ProfileMemory(Base):
    """
    SQLAlchemy model for storing user profile memory.

    Attributes:
        id (int): Primary key.
        user_id (int): Unique identifier for the user.
        data (str): Serialized user data.
        created_at (datetime): Timestamp of creation.
    """

    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    learning_progress = relationship(
        'LearningProgress', back_populates='profile_memory', uselist=False
    )
    user_preferences = relationship(
        'UserPreferences', back_populates='profile_memory', uselist=False
    )


class LearningProgress(Base):
    """
    SQLAlchemy model for user learning progress.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        progress_data (str): Serialized progress data.
        updated_at (datetime): Timestamp of last update.
    """

    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    progress_data = Column(Text)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile_memory = relationship(
        'ProfileMemory', back_populates='learning_progress'
    )


class UserPreferences(Base):
    """
    SQLAlchemy model for user preferences.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        preferences_data (str): Serialized preferences data.
        updated_at (datetime): Timestamp of last update.
    """

    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    preferences_data = Column(Text)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profile_memory = relationship(
        'ProfileMemory', back_populates='user_preferences'
    )


# Pydantic Models for Validation
class ProfileMemoryBase(BaseModel):
    user_id: int
    data: str

    @validator('user_id')
    def user_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('user_id must be positive')
        return v


class ProfileMemoryCreate(ProfileMemoryBase):
    """
    Model for creating ProfileMemory.
    """


class ProfileMemoryUpdate(BaseModel):
    data: str


class ProfileMemoryOut(ProfileMemoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LearningProgressBase(BaseModel):
    progress_data: str


class LearningProgressCreate(LearningProgressBase):
    """
    Model for creating LearningProgress.
    """


class LearningProgressUpdate(LearningProgressBase):
    """
    Model for updating LearningProgress.
    """


class LearningProgressOut(LearningProgressBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class UserPreferencesBase(BaseModel):
    preferences_data: str


class UserPreferencesCreate(UserPreferencesBase):
    """
    Model for creating UserPreferences.
    """


class UserPreferencesUpdate(UserPreferencesBase):
    """
    Model for updating UserPreferences.
    """


class UserPreferencesOut(UserPreferencesBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


# Service Classes
class ProfileMemoryService:
    """
    Service class for ProfileMemory operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the ProfileMemoryService with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session

    async def create_profile_memory(
        self, profile: ProfileMemoryCreate
    ) -> ProfileMemoryOut:
        """
        Create a new ProfileMemory entry.

        Args:
            profile (ProfileMemoryCreate): Profile data.

        Returns:
            ProfileMemoryOut: Created profile memory.

        Raises:
            Exception: If creation fails.

        Example:
            >>> async def test_create():
            ...     session = AsyncSession(...)
            ...     service = ProfileMemoryService(session)
            ...     profile = ProfileMemoryCreate(user_id=1, data="{}")
            ...     result = await service.create_profile_memory(profile)
            ...     assert result.user_id == 1
        """
        new_profile = ProfileMemory(
            user_id=profile.user_id,
            data=profile.data,
        )
        self.session.add(new_profile)
        try:
            await self.session.commit()
            await self.session.refresh(new_profile)
            logger.info(f"Created ProfileMemory for user_id {profile.user_id}")
            return ProfileMemoryOut.from_orm(new_profile)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating ProfileMemory: {e}")
            raise

    async def get_profile_memory(
        self, user_id: int
    ) -> Optional[ProfileMemoryOut]:
        """
        Retrieve a ProfileMemory by user_id.

        Args:
            user_id (int): The user ID.

        Returns:
            Optional[ProfileMemoryOut]: The profile memory if found, else None.

        Example:
            >>> async def test_get():
            ...     session = AsyncSession(...)
            ...     service = ProfileMemoryService(session)
            ...     result = await service.get_profile_memory(1)
            ...     if result:
            ...         assert result.user_id == 1
        """
        result = await self.session.execute(
            select(ProfileMemory).where(ProfileMemory.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            logger.info(f"Retrieved ProfileMemory for user_id {user_id}")
            return ProfileMemoryOut.from_orm(profile)
        else:
            logger.warning(f"ProfileMemory not found for user_id {user_id}")
            return None

    async def update_profile_memory(
        self, user_id: int, profile_data: ProfileMemoryUpdate
    ) -> Optional[ProfileMemoryOut]:
        """
        Update a ProfileMemory entry.

        Args:
            user_id (int): The user ID.
            profile_data (ProfileMemoryUpdate): Updated profile data.

        Returns:
            Optional[ProfileMemoryOut]: The updated profile memory if successful, else None.

        Raises:
            Exception: If update fails.

        Example:
            >>> async def test_update():
            ...     session = AsyncSession(...)
            ...     service = ProfileMemoryService(session)
            ...     update_data = ProfileMemoryUpdate(data='{"key": "value"}')
            ...     result = await service.update_profile_memory(1, update_data)
            ...     if result:
            ...         assert result.data == '{"key": "value"}'
        """
        result = await self.session.execute(
            select(ProfileMemory).where(ProfileMemory.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            logger.warning(f"ProfileMemory not found for user_id {user_id}")
            return None
        try:
            profile.data = profile_data.data
            await self.session.commit()
            await self.session.refresh(profile)
            logger.info(f"Updated ProfileMemory for user_id {user_id}")
            return ProfileMemoryOut.from_orm(profile)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating ProfileMemory: {e}")
            raise

    async def delete_profile_memory(self, user_id: int) -> bool:
        """
        Delete a ProfileMemory entry.

        Args:
            user_id (int): The user ID.

        Returns:
            bool: True if deleted, False otherwise.

        Raises:
            Exception: If deletion fails.

        Example:
            >>> async def test_delete():
            ...     session = AsyncSession(...)
            ...     service = ProfileMemoryService(session)
            ...     success = await service.delete_profile_memory(1)
            ...     assert success
        """
        result = await self.session.execute(
            select(ProfileMemory).where(ProfileMemory.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            logger.warning(f"ProfileMemory not found for user_id {user_id}")
            return False
        try:
            await self.session.delete(profile)
            await self.session.commit()
            logger.info(f"Deleted ProfileMemory for user_id {user_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting ProfileMemory: {e}")
            raise


class LearningProgressService:
    """
    Service class for LearningProgress operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the LearningProgressService with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session

    async def create_learning_progress(
        self, profile_memory_id: int, progress: LearningProgressCreate
    ) -> LearningProgressOut:
        """
        Create a new LearningProgress entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.
            progress (LearningProgressCreate): Progress data.

        Returns:
            LearningProgressOut: Created learning progress.

        Raises:
            Exception: If creation fails.
        """
        new_progress = LearningProgress(
            profile_memory_id=profile_memory_id,
            progress_data=progress.progress_data,
        )
        self.session.add(new_progress)
        try:
            await self.session.commit()
            await self.session.refresh(new_progress)
            logger.info(
                f"Created LearningProgress for profile_memory_id {profile_memory_id}"
            )
            return LearningProgressOut.from_orm(new_progress)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating LearningProgress: {e}")
            raise

    async def get_learning_progress(
        self, profile_memory_id: int
    ) -> Optional[LearningProgressOut]:
        """
        Retrieve LearningProgress by profile_memory_id.

        Args:
            profile_memory_id (int): The ProfileMemory ID.

        Returns:
            Optional[LearningProgressOut]: The learning progress if found, else None.
        """
        result = await self.session.execute(
            select(LearningProgress).where(
                LearningProgress.profile_memory_id == profile_memory_id
            )
        )
        progress = result.scalar_one_or_none()
        if progress:
            logger.info(
                f"Retrieved LearningProgress for profile_memory_id {profile_memory_id}"
            )
            return LearningProgressOut.from_orm(progress)
        else:
            logger.warning(
                f"LearningProgress not found for profile_memory_id {profile_memory_id}"
            )
            return None

    async def update_learning_progress(
        self,
        profile_memory_id: int,
        progress_data: LearningProgressUpdate,
    ) -> Optional[LearningProgressOut]:
        """
        Update a LearningProgress entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.
            progress_data (LearningProgressUpdate): Updated progress data.

        Returns:
            Optional[LearningProgressOut]: The updated learning progress if successful, else None.

        Raises:
            Exception: If update fails.
        """
        result = await self.session.execute(
            select(LearningProgress).where(
                LearningProgress.profile_memory_id == profile_memory_id
            )
        )
        progress = result.scalar_one_or_none()
        if not progress:
            logger.warning(
                f"LearningProgress not found for profile_memory_id {profile_memory_id}"
            )
            return None
        try:
            progress.progress_data = progress_data.progress_data
            await self.session.commit()
            await self.session.refresh(progress)
            logger.info(
                f"Updated LearningProgress for profile_memory_id {profile_memory_id}"
            )
            return LearningProgressOut.from_orm(progress)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating LearningProgress: {e}")
            raise

    async def delete_learning_progress(self, profile_memory_id: int) -> bool:
        """
        Delete a LearningProgress entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.

        Returns:
            bool: True if deleted, False otherwise.

        Raises:
            Exception: If deletion fails.
        """
        result = await self.session.execute(
            select(LearningProgress).where(
                LearningProgress.profile_memory_id == profile_memory_id
            )
        )
        progress = result.scalar_one_or_none()
        if not progress:
            logger.warning(
                f"LearningProgress not found for profile_memory_id {profile_memory_id}"
            )
            return False
        try:
            await self.session.delete(progress)
            await self.session.commit()
            logger.info(
                f"Deleted LearningProgress for profile_memory_id {profile_memory_id}"
            )
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting LearningProgress: {e}")
            raise


class UserPreferencesService:
    """
    Service class for UserPreferences operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserPreferencesService with a database session.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session

    async def create_user_preferences(
        self, profile_memory_id: int, preferences: UserPreferencesCreate
    ) -> UserPreferencesOut:
        """
        Create a new UserPreferences entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.
            preferences (UserPreferencesCreate): Preferences data.

        Returns:
            UserPreferencesOut: Created user preferences.

        Raises:
            Exception: If creation fails.
        """
        new_preferences = UserPreferences(
            profile_memory_id=profile_memory_id,
            preferences_data=preferences.preferences_data,
        )
        self.session.add(new_preferences)
        try:
            await self.session.commit()
            await self.session.refresh(new_preferences)
            logger.info(
                f"Created UserPreferences for profile_memory_id {profile_memory_id}"
            )
            return UserPreferencesOut.from_orm(new_preferences)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating UserPreferences: {e}")
            raise

    async def get_user_preferences(
        self, profile_memory_id: int
    ) -> Optional[UserPreferencesOut]:
        """
        Retrieve UserPreferences by profile_memory_id.

        Args:
            profile_memory_id (int): The ProfileMemory ID.

        Returns:
            Optional[UserPreferencesOut]: The user preferences if found, else None.
        """
        result = await self.session.execute(
            select(UserPreferences).where(
                UserPreferences.profile_memory_id == profile_memory_id
            )
        )
        preferences = result.scalar_one_or_none()
        if preferences:
            logger.info(
                f"Retrieved UserPreferences for profile_memory_id {profile_memory_id}"
            )
            return UserPreferencesOut.from_orm(preferences)
        else:
            logger.warning(
                f"UserPreferences not found for profile_memory_id {profile_memory_id}"
            )
            return None

    async def update_user_preferences(
        self,
        profile_memory_id: int,
        preferences_data: UserPreferencesUpdate,
    ) -> Optional[UserPreferencesOut]:
        """
        Update a UserPreferences entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.
            preferences_data (UserPreferencesUpdate): Updated preferences data.

        Returns:
            Optional[UserPreferencesOut]: The updated user preferences if successful, else None.

        Raises:
            Exception: If update fails.
        """
        result = await self.session.execute(
            select(UserPreferences).where(
                UserPreferences.profile_memory_id == profile_memory_id
            )
        )
        preferences = result.scalar_one_or_none()
        if not preferences:
            logger.warning(
                f"UserPreferences not found for profile_memory_id {profile_memory_id}"
            )
            return None
        try:
            preferences.preferences_data = preferences_data.preferences_data
            await self.session.commit()
            await self.session.refresh(preferences)
            logger.info(
                f"Updated UserPreferences for profile_memory_id {profile_memory_id}"
            )
            return UserPreferencesOut.from_orm(preferences)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating UserPreferences: {e}")
            raise

    async def delete_user_preferences(self, profile_memory_id: int) -> bool:
        """
        Delete a UserPreferences entry.

        Args:
            profile_memory_id (int): The ProfileMemory ID.

        Returns:
            bool: True if deleted, False otherwise.

        Raises:
            Exception: If deletion fails.
        """
        result = await self.session.execute(
            select(UserPreferences).where(
                UserPreferences.profile_memory_id == profile_memory_id
            )
        )
        preferences = result.scalar_one_or_none()
        if not preferences:
            logger.warning(
                f"UserPreferences not found for profile_memory_id {profile_memory_id}"
            )
            return False
        try:
            await self.session.delete(preferences)
            await self.session.commit()
            logger.info(
                f"Deleted UserPreferences for profile_memory_id {profile_memory_id}"
            )
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting UserPreferences: {e}")
            raise


# Example usage (to be used within an async context)
async def main():
    """
    Example asynchronous function demonstrating the usage of services.
    """
    # Assuming `async_session` is an instance of AsyncSession
    async with AsyncSession(...) as session:
        profile_service = ProfileMemoryService(session)
        progress_service = LearningProgressService(session)
        preferences_service = UserPreferencesService(session)

        # Create a new profile memory
        profile = ProfileMemoryCreate(user_id=1, data='{"name": "John Doe"}')
        created_profile = await profile_service.create_profile_memory(profile)

        # Update profile memory
        update_data = ProfileMemoryUpdate(data='{"name": "Jane Doe"}')
        updated_profile = await profile_service.update_profile_memory(
            user_id=1, profile_data=update_data
        )

        # Get profile memory
        retrieved_profile = await profile_service.get_profile_memory(user_id=1)

        # Delete profile memory
        deleted = await profile_service.delete_profile_memory(user_id=1)

# Uncomment below lines to run the example when the module is executed directly
# if __name__ == "__main__":
#     asyncio.run(main())