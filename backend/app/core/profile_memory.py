import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL (using SQLite for demonstration; replace with your DB URL)
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Base model for SQLAlchemy
Base = declarative_base()

# ---------------------------
# SQLAlchemy Models
# ---------------------------

class ProfileMemory(Base):
    """
    SQLAlchemy model for user profile storage.
    """
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    learning_progress = relationship(
        "LearningProgress", back_populates="profile", uselist=False
    )
    user_preferences = relationship(
        "UserPreferences", back_populates="profile", uselist=False
    )


class LearningProgress(Base):
    """
    SQLAlchemy model for storing user's learning progress.
    """
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey('profile_memory.id'), nullable=False
    )
    progress_data = Column(Text, nullable=True)

    # Relationships
    profile = relationship(
        "ProfileMemory", back_populates="learning_progress"
    )


class UserPreferences(Base):
    """
    SQLAlchemy model for storing user's preferences.
    """
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey('profile_memory.id'), nullable=False
    )
    preferences_data = Column(Text, nullable=True)

    # Relationships
    profile = relationship(
        "ProfileMemory", back_populates="user_preferences"
    )

# ---------------------------
# Pydantic Models
# ---------------------------

# ProfileMemory Schemas

class ProfileMemoryBase(BaseModel):
    user_id: str = Field(..., max_length=50)


class ProfileMemoryCreate(ProfileMemoryBase):
    pass


class ProfileMemoryUpdate(ProfileMemoryBase):
    pass


class ProfileMemoryInDB(ProfileMemoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# LearningProgress Schemas

class LearningProgressBase(BaseModel):
    progress_data: Optional[str] = None


class LearningProgressCreate(LearningProgressBase):
    profile_id: int


class LearningProgressUpdate(LearningProgressBase):
    pass


class LearningProgressInDB(LearningProgressBase):
    id: int
    profile_id: int

    class Config:
        orm_mode = True

# UserPreferences Schemas

class UserPreferencesBase(BaseModel):
    preferences_data: Optional[str] = None


class UserPreferencesCreate(UserPreferencesBase):
    profile_id: int


class UserPreferencesUpdate(UserPreferencesBase):
    pass


class UserPreferencesInDB(UserPreferencesBase):
    id: int
    profile_id: int

    class Config:
        orm_mode = True

# ---------------------------
# Repository Classes
# ---------------------------

class ProfileMemoryRepository:
    """
    Repository for ProfileMemory model.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db_session (AsyncSession): The async database session.
        """
        self.db_session = db_session

    async def get_by_user_id(self, user_id: str) -> Optional[ProfileMemory]:
        """
        Get ProfileMemory by user_id.

        Args:
            user_id (str): The user ID.

        Returns:
            Optional[ProfileMemory]: The ProfileMemory instance or None.

        >>> import asyncio
        >>> async def test_get_by_user_id():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.get_by_user_id("nonexistent_user")
        ...         assert profile is None
        ...
        >>> asyncio.run(test_get_by_user_id())
        """
        try:
            result = await self.db_session.execute(
                select(ProfileMemory).where(ProfileMemory.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            return profile
        except Exception as e:
            logger.error(f"Error fetching ProfileMemory by user_id {user_id}: {e}")
            return None

    async def create(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """
        Create a new ProfileMemory.

        Args:
            profile_data (ProfileMemoryCreate): The profile data.

        Returns:
            ProfileMemory: The created ProfileMemory instance.

        >>> import asyncio
        >>> async def test_create():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.create(ProfileMemoryCreate(user_id="user123"))
        ...         assert profile.user_id == "user123"
        ...
        >>> asyncio.run(test_create())
        """
        new_profile = ProfileMemory(user_id=profile_data.user_id)
        self.db_session.add(new_profile)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_profile)
            return new_profile
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating ProfileMemory: {e}")
            raise

    async def update(
        self, profile: ProfileMemory, update_data: ProfileMemoryUpdate
    ) -> ProfileMemory:
        """
        Update an existing ProfileMemory.

        Args:
            profile (ProfileMemory): The existing ProfileMemory instance.
            update_data (ProfileMemoryUpdate): The update data.

        Returns:
            ProfileMemory: The updated ProfileMemory instance.

        >>> import asyncio
        >>> async def test_update():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.create(ProfileMemoryCreate(user_id="user_to_update"))
        ...         update_data = ProfileMemoryUpdate(user_id="updated_user")
        ...         updated_profile = await repo.update(profile, update_data)
        ...         assert updated_profile.user_id == "updated_user"
        ...
        >>> asyncio.run(test_update())
        """
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(profile)
            return profile
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating ProfileMemory id {profile.id}: {e}")
            raise

    async def delete(self, profile: ProfileMemory) -> None:
        """
        Delete a ProfileMemory.

        Args:
            profile (ProfileMemory): The ProfileMemory instance to delete.

        Returns:
            None

        >>> import asyncio
        >>> async def test_delete():
        ...     async with async_session() as session:
        ...         repo = ProfileMemoryRepository(session)
        ...         profile = await repo.create(ProfileMemoryCreate(user_id="user_to_delete"))
        ...         await repo.delete(profile)
        ...         deleted_profile = await repo.get_by_user_id("user_to_delete")
        ...         assert deleted_profile is None
        ...
        >>> asyncio.run(test_delete())
        """
        try:
            await self.db_session.delete(profile)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting ProfileMemory id {profile.id}: {e}")
            raise

class LearningProgressRepository:
    """
    Repository for LearningProgress model.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_profile_id(
        self, profile_id: int
    ) -> Optional[LearningProgress]:
        """
        Get LearningProgress by profile_id.

        Args:
            profile_id (int): The profile ID.

        Returns:
            Optional[LearningProgress]: The LearningProgress instance or None.
        """
        try:
            result = await self.db_session.execute(
                select(LearningProgress).where(
                    LearningProgress.profile_id == profile_id
                )
            )
            progress = result.scalar_one_or_none()
            return progress
        except Exception as e:
            logger.error(
                f"Error fetching LearningProgress by profile_id {profile_id}: {e}"
            )
            return None

    async def create(
        self, progress_data: LearningProgressCreate
    ) -> LearningProgress:
        """
        Create LearningProgress for a profile.

        Args:
            progress_data (LearningProgressCreate): The progress data.

        Returns:
            LearningProgress: The created LearningProgress instance.
        """
        new_progress = LearningProgress(
            profile_id=progress_data.profile_id,
            progress_data=progress_data.progress_data,
        )
        self.db_session.add(new_progress)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_progress)
            return new_progress
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating LearningProgress: {e}")
            raise

    async def update(
        self,
        progress: LearningProgress,
        update_data: LearningProgressUpdate,
    ) -> LearningProgress:
        """
        Update an existing LearningProgress.

        Args:
            progress (LearningProgress): The existing LearningProgress instance.
            update_data (LearningProgressUpdate): The update data.

        Returns:
            LearningProgress: The updated LearningProgress instance.
        """
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(progress, field, value)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(progress)
            return progress
        except Exception as e:
            await self.db_session.rollback()
            logger.error(
                f"Error updating LearningProgress id {progress.id}: {e}"
            )
            raise

    async def delete(self, progress: LearningProgress) -> None:
        """
        Delete a LearningProgress.

        Args:
            progress (LearningProgress): The LearningProgress instance to delete.

        Returns:
            None
        """
        try:
            await self.db_session.delete(progress)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(
                f"Error deleting LearningProgress id {progress.id}: {e}"
            )
            raise

class UserPreferencesRepository:
    """
    Repository for UserPreferences model.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_profile_id(
        self, profile_id: int
    ) -> Optional[UserPreferences]:
        """
        Get UserPreferences by profile_id.

        Args:
            profile_id (int): The profile ID.

        Returns:
            Optional[UserPreferences]: The UserPreferences instance or None.
        """
        try:
            result = await self.db_session.execute(
                select(UserPreferences).where(
                    UserPreferences.profile_id == profile_id
                )
            )
            preferences = result.scalar_one_or_none()
            return preferences
        except Exception as e:
            logger.error(
                f"Error fetching UserPreferences by profile_id {profile_id}: {e}"
            )
            return None

    async def create(
        self, preferences_data: UserPreferencesCreate
    ) -> UserPreferences:
        """
        Create UserPreferences for a profile.

        Args:
            preferences_data (UserPreferencesCreate): The preferences data.

        Returns:
            UserPreferences: The created UserPreferences instance.
        """
        new_preferences = UserPreferences(
            profile_id=preferences_data.profile_id,
            preferences_data=preferences_data.preferences_data,
        )
        self.db_session.add(new_preferences)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_preferences)
            return new_preferences
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating UserPreferences: {e}")
            raise

    async def update(
        self,
        preferences: UserPreferences,
        update_data: UserPreferencesUpdate,
    ) -> UserPreferences:
        """
        Update an existing UserPreferences.

        Args:
            preferences (UserPreferences): The existing UserPreferences instance.
            update_data (UserPreferencesUpdate): The update data.

        Returns:
            UserPreferences: The updated UserPreferences instance.
        """
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preferences, field, value)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(preferences)
            return preferences
        except Exception as e:
            await self.db_session.rollback()
            logger.error(
                f"Error updating UserPreferences id {preferences.id}: {e}"
            )
            raise

    async def delete(self, preferences: UserPreferences) -> None:
        """
        Delete a UserPreferences.

        Args:
            preferences (UserPreferences): The UserPreferences instance to delete.

        Returns:
            None
        """
        try:
            await self.db_session.delete(preferences)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            logger.error(
                f"Error deleting UserPreferences id {preferences.id}: {e}"
            )
            raise

# ---------------------------
# Database Initialization
# ---------------------------

async def init_db():
    """
    Initialize the database by creating all tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")

# ---------------------------
# Main Execution
# ---------------------------

if __name__ == "__main__":
    async def main():
        """
        Main function to initialize the database and run doctests.
        """
        await init_db()
        # Run doctests
        import doctest
        doctest.testmod()

    asyncio.run(main())