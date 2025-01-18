# backend/app/core/profile_memory.py

from typing import List, Optional
from datetime import datetime
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, select

from pydantic import BaseModel, validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy base class
Base = declarative_base()

# Async database engine and session
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    DATABASE_URL, echo=False
)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Models

class ProfileMemory(Base):
    """
    ORM model for storing user profile memory.

    Attributes:
        id (int): Primary key.
        user_id (int): Unique identifier for the user.
        created_at (datetime): Timestamp of creation.
        learning_progress (LearningProgress): Associated learning progress.
        user_preferences (UserPreferences): Associated user preferences.
    """
    __tablename__ = 'profile_memories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    learning_progress = relationship("LearningProgress", back_populates="profile_memory", uselist=False)
    user_preferences = relationship("UserPreferences", back_populates="profile_memory", uselist=False)

class LearningProgress(Base):
    """
    ORM model for storing user's learning progress.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        progress_data (str): JSON or text data representing progress.
        updated_at (datetime): Timestamp of last update.
    """
    __tablename__ = 'learning_progresses'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memories.id'), nullable=False)
    progress_data = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_memory = relationship("ProfileMemory", back_populates="learning_progress")

class UserPreferences(Base):
    """
    ORM model for storing user's preferences.

    Attributes:
        id (int): Primary key.
        profile_memory_id (int): Foreign key to ProfileMemory.
        preferences_data (str): JSON or text data representing preferences.
        updated_at (datetime): Timestamp of last update.
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memories.id'), nullable=False)
    preferences_data = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_memory = relationship("ProfileMemory", back_populates="user_preferences")

# Pydantic models for validation

class LearningProgressCreate(BaseModel):
    progress_data: str

    @validator('progress_data')
    def validate_progress_data(cls, v):
        if not v.strip():
            raise ValueError('progress_data cannot be empty')
        return v

class UserPreferencesCreate(BaseModel):
    preferences_data: str

    @validator('preferences_data')
    def validate_preferences_data(cls, v):
        if not v.strip():
            raise ValueError('preferences_data cannot be empty')
        return v

class ProfileMemoryCreate(BaseModel):
    user_id: int
    learning_progress: Optional[LearningProgressCreate] = None
    user_preferences: Optional[UserPreferencesCreate] = None

    @validator('user_id')
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('user_id must be positive')
        return v

class LearningProgressRead(BaseModel):
    id: int
    progress_data: str
    updated_at: datetime

    class Config:
        orm_mode = True

class UserPreferencesRead(BaseModel):
    id: int
    preferences_data: str
    updated_at: datetime

    class Config:
        orm_mode = True

class ProfileMemoryRead(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    learning_progress: Optional[LearningProgressRead] = None
    user_preferences: Optional[UserPreferencesRead] = None

    class Config:
        orm_mode = True

# Repository pattern for database operations

class ProfileMemoryRepository:
    """
    Repository for ProfileMemory operations.

    Methods:
        create_profile_memory: Create a new profile memory.
        get_profile_memory: Retrieve a profile memory by user_id.
        update_profile_memory: Update existing profile memory.
        delete_profile_memory: Delete a profile memory.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile_memory(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new ProfileMemory.

        :param profile_data: Data required to create ProfileMemory
        :return: Created ProfileMemory object

        >>> import asyncio
        >>> async def test_create():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile_input = ProfileMemoryCreate(
        ...             user_id=1,
        ...             learning_progress=LearningProgressCreate(progress_data='{"level": 1}'),
        ...             user_preferences=UserPreferencesCreate(preferences_data='{"theme": "dark"}')
        ...         )
        ...         profile = await repo.create_profile_memory(profile_input)
        ...         assert profile.user_id == 1
        ...         await session.commit()
        ...     await engine.dispose()
        >>> asyncio.run(test_create())
        """
        try:
            new_profile = ProfileMemory(user_id=profile_data.user_id)
            self.session.add(new_profile)
            await self.session.flush()  # Ensure new_profile.id is available

            if profile_data.learning_progress:
                lp = LearningProgress(
                    profile_memory_id=new_profile.id,
                    progress_data=profile_data.learning_progress.progress_data
                )
                self.session.add(lp)

            if profile_data.user_preferences:
                up = UserPreferences(
                    profile_memory_id=new_profile.id,
                    preferences_data=profile_data.user_preferences.preferences_data
                )
                self.session.add(up)

            await self.session.commit()
            await self.session.refresh(new_profile)
            logger.info(f"Created ProfileMemory for user_id {profile_data.user_id}")
            return new_profile
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create ProfileMemory: {e}")
            raise

    async def get_profile_memory(self, user_id: int) -> Optional[ProfileMemory]:
        """
        Get ProfileMemory by user_id.

        :param user_id: User ID
        :return: ProfileMemory object or None

        >>> import asyncio
        >>> async def test_get():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.get_profile_memory(user_id=1)
        ...         if profile:
        ...             assert profile.user_id == 1
        ...     await engine.dispose()
        >>> asyncio.run(test_get())
        """
        try:
            result = await self.session.execute(
                select(ProfileMemory).where(ProfileMemory.user_id == user_id)
                .options(
                    relationship(ProfileMemory.learning_progress),
                    relationship(ProfileMemory.user_preferences)
                )
            )
            profile = result.scalars().first()
            if profile:
                logger.info(f"Retrieved ProfileMemory for user_id {user_id}")
            else:
                logger.warning(f"No ProfileMemory found for user_id {user_id}")
            return profile
        except Exception as e:
            logger.error(f"Failed to retrieve ProfileMemory: {e}")
            raise

    async def update_profile_memory(self, user_id: int, profile_data: ProfileMemoryCreate) -> Optional[ProfileMemory]:
        """
        Update an existing ProfileMemory.

        :param user_id: User ID
        :param profile_data: Data to update
        :return: Updated ProfileMemory object or None

        >>> import asyncio
        >>> async def test_update():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile_input = ProfileMemoryCreate(
        ...             user_id=1,
        ...             learning_progress=LearningProgressCreate(progress_data='{"level": 2}'),
        ...             user_preferences=UserPreferencesCreate(preferences_data='{"theme": "light"}')
        ...         )
        ...         profile = await repo.update_profile_memory(1, profile_input)
        ...         assert profile.learning_progress.progress_data == '{"level": 2}'
        ...         await session.commit()
        ...     await engine.dispose()
        >>> asyncio.run(test_update())
        """
        try:
            profile = await self.get_profile_memory(user_id)
            if not profile:
                logger.warning(f"No ProfileMemory found for user_id {user_id}")
                return None

            if profile_data.learning_progress:
                if profile.learning_progress:
                    profile.learning_progress.progress_data = profile_data.learning_progress.progress_data
                else:
                    lp = LearningProgress(
                        profile_memory_id=profile.id,
                        progress_data=profile_data.learning_progress.progress_data
                    )
                    self.session.add(lp)

            if profile_data.user_preferences:
                if profile.user_preferences:
                    profile.user_preferences.preferences_data = profile_data.user_preferences.preferences_data
                else:
                    up = UserPreferences(
                        profile_memory_id=profile.id,
                        preferences_data=profile_data.user_preferences.preferences_data
                    )
                    self.session.add(up)

            await self.session.commit()
            await self.session.refresh(profile)
            logger.info(f"Updated ProfileMemory for user_id {user_id}")
            return profile
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update ProfileMemory: {e}")
            raise

    async def delete_profile_memory(self, user_id: int) -> bool:
        """
        Delete a ProfileMemory by user_id.

        :param user_id: User ID
        :return: True if deleted, False otherwise

        >>> import asyncio
        >>> async def test_delete():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         success = await repo.delete_profile_memory(1)
        ...         assert success is True
        ...         await session.commit()
        ...     await engine.dispose()
        >>> asyncio.run(test_delete())
        """
        try:
            profile = await self.get_profile_memory(user_id)
            if not profile:
                logger.warning(f"No ProfileMemory found for user_id {user_id}")
                return False

            await self.session.delete(profile)
            await self.session.commit()
            logger.info(f"Deleted ProfileMemory for user_id {user_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete ProfileMemory: {e}")
            raise

# Asynchronous initialization function to create tables (for testing purposes)
async def init_models():
    """
    Initialize database models.

    >>> import asyncio
    >>> async def test_init_models():
    ...     await init_models()
    ...     # Check if tables are created (this is just an example)
    ...     assert True
    ...     await engine.dispose()
    >>> asyncio.run(test_init_models())
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Initialized database models.")

# Example usage (can be removed in production)

if __name__ == "__main__":
    async def main():
        await init_models()

        # Create a profile memory
        async with async_session() as session:
            repo = ProfileMemoryRepository(session)
            profile_input = ProfileMemoryCreate(
                user_id=1,
                learning_progress=LearningProgressCreate(progress_data='{"level": 1}'),
                user_preferences=UserPreferencesCreate(preferences_data='{"theme": "dark"}')
            )
            profile = await repo.create_profile_memory(profile_input)
            print("Created ProfileMemory:", ProfileMemoryRead.from_orm(profile))

        # Get the profile memory
        async with async_session() as session:
            repo = ProfileMemoryRepository(session)
            profile = await repo.get_profile_memory(user_id=1)
            if profile:
                print("Retrieved ProfileMemory:", ProfileMemoryRead.from_orm(profile))
            else:
                print("ProfileMemory not found.")

    asyncio.run(main())