import asyncio
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, ValidationError, validator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship,
    selectinload,
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.future import select

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Example using SQLite database

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session_factory = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Models
class ProfileMemory(Base):
    __tablename__ = "profile_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    learning_progress = relationship(
        "LearningProgress",
        back_populates="profile_memory",
        uselist=False,
        lazy="selectin",
    )
    user_preferences = relationship(
        "UserPreferences",
        back_populates="profile_memory",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self):
        return f"<ProfileMemory(user_id={self.user_id})>"


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey("profile_memory.id"))
    progress_data = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    profile_memory = relationship(
        "ProfileMemory", back_populates="learning_progress"
    )

    def __repr__(self):
        return f"<LearningProgress(profile_memory_id={self.profile_memory_id})>"


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey("profile_memory.id"))
    preferences_data = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

    profile_memory = relationship(
        "ProfileMemory", back_populates="user_preferences"
    )

    def __repr__(self):
        return f"<UserPreferences(profile_memory_id={self.profile_memory_id})>"


# Pydantic Models
class LearningProgressCreate(BaseModel):
    progress_data: str = Field(..., max_length=500)

    @validator("progress_data")
    def validate_progress_data(cls, v):
        if not v:
            raise ValueError("Progress data cannot be empty")
        return v


class UserPreferencesCreate(BaseModel):
    preferences_data: str = Field(..., max_length=500)

    @validator("preferences_data")
    def validate_preferences_data(cls, v):
        if not v:
            raise ValueError("Preferences data cannot be empty")
        return v


class ProfileMemoryCreate(BaseModel):
    user_id: int
    learning_progress: Optional[LearningProgressCreate] = None
    user_preferences: Optional[UserPreferencesCreate] = None

    @validator("user_id")
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v


class LearningProgressOut(BaseModel):
    id: int
    progress_data: str
    last_updated: datetime

    class Config:
        orm_mode = True


class UserPreferencesOut(BaseModel):
    id: int
    preferences_data: str
    updated_at: datetime

    class Config:
        orm_mode = True


class ProfileMemoryOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    learning_progress: Optional[LearningProgressOut] = None
    user_preferences: Optional[UserPreferencesOut] = None

    class Config:
        orm_mode = True


# FastAPI app
app = FastAPI()


# Dependency to get DB session
async def get_db():
    async_session = async_session_factory()
    try:
        yield async_session
    finally:
        await async_session.close()


@app.on_event("startup")
async def startup():
    """
    Startup event to create database tables.
    """
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


@app.post("/profile_memory/", response_model=ProfileMemoryOut)
async def create_profile_memory(
    profile_memory_in: ProfileMemoryCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new ProfileMemory record along with associated LearningProgress and UserPreferences.

    :param profile_memory_in: ProfileMemoryCreate
    :param db: AsyncSession
    :return: ProfileMemoryOut

    Example:
        >>> import asyncio
        >>> from sqlalchemy.ext.asyncio import AsyncSession
        >>> async def test_create_profile_memory():
        ...     from profile_memory import (
        ...         create_profile_memory,
        ...         ProfileMemoryCreate,
        ...         LearningProgressCreate,
        ...         UserPreferencesCreate,
        ...         get_db,
        ...     )
        ...     profile_memory_in = ProfileMemoryCreate(
        ...         user_id=1,
        ...         learning_progress=LearningProgressCreate(progress_data='{"lesson": 1}'),
        ...         user_preferences=UserPreferencesCreate(preferences_data='{"theme": "dark"}'),
        ...     )
        ...     async for db in get_db():
        ...         result = await create_profile_memory(profile_memory_in, db)
        ...         assert result.user_id == 1
        >>> asyncio.run(test_create_profile_memory())
    """
    try:
        profile_memory = ProfileMemory(user_id=profile_memory_in.user_id)
        db.add(profile_memory)
        await db.commit()
        await db.refresh(profile_memory)
    except Exception as e:
        logger.error(f"Error creating ProfileMemory: {e}")
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error creating ProfileMemory")

    if profile_memory_in.learning_progress:
        learning_progress = LearningProgress(
            profile_memory_id=profile_memory.id,
            progress_data=profile_memory_in.learning_progress.progress_data,
        )
        db.add(learning_progress)

    if profile_memory_in.user_preferences:
        user_preferences = UserPreferences(
            profile_memory_id=profile_memory.id,
            preferences_data=profile_memory_in.user_preferences.preferences_data,
        )
        db.add(user_preferences)

    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Error creating associated records: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=400, detail="Error creating associated records"
        )

    await db.refresh(profile_memory)

    return profile_memory


@app.get("/profile_memory/{user_id}", response_model=ProfileMemoryOut)
async def get_profile_memory(
    user_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve ProfileMemory by user_id.

    :param user_id: int
    :param db: AsyncSession
    :return: ProfileMemoryOut

    Example:
        >>> import asyncio
        >>> async def test_get_profile_memory():
        ...     from profile_memory import get_profile_memory, get_db
        ...     async for db in get_db():
        ...         result = await get_profile_memory(1, db)
        ...         assert result.user_id == 1
        >>> asyncio.run(test_get_profile_memory())
    """
    result = await db.execute(
        select(ProfileMemory)
        .options(
            selectinload(ProfileMemory.learning_progress),
            selectinload(ProfileMemory.user_preferences),
        )
        .where(ProfileMemory.user_id == user_id)
    )
    profile_memory = result.scalars().first()
    if not profile_memory:
        raise HTTPException(status_code=404, detail="ProfileMemory not found")
    return profile_memory