"""
Profile Memory Manager

This module provides user profile storage, learning progress, and user preferences
management using SQLAlchemy with asyncio support.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from .database import Base

logger = logging.getLogger(__name__)

# SQLAlchemy Models
class ProfileMemory(Base):
    """SQLAlchemy model for storing user profile information."""
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    learning_progress = relationship("LearningProgress", back_populates="profile_memory", uselist=False)
    preferences = relationship("UserPreferences", back_populates="profile_memory", uselist=False)

class LearningProgress(Base):
    """SQLAlchemy model for storing user's learning progress."""
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    progress_data = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_memory = relationship("ProfileMemory", back_populates="learning_progress")

class UserPreferences(Base):
    """SQLAlchemy model for storing user's preferences."""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    preferences_data = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_memory = relationship("ProfileMemory", back_populates="preferences")

# Pydantic Models
class LearningProgressCreate(BaseModel):
    progress_data: str

class UserPreferencesCreate(BaseModel):
    preferences_data: str

class ProfileMemoryCreate(BaseModel):
    user_id: int
    learning_progress: Optional[LearningProgressCreate] = None
    preferences: Optional[UserPreferencesCreate] = None

class ProfileMemoryOut(BaseModel):
    user_id: int
    created_at: datetime
    updated_at: datetime
    learning_progress: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Repository Class
class ProfileMemoryRepository:
    """Repository class for ProfileMemory operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile_by_user_id(self, user_id: int) -> Optional[ProfileMemory]:
        """Get a profile by user_id."""
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
        """Create a new profile with associated learning progress and preferences."""
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

    async def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[ProfileMemory]:
        """Update an existing profile."""
        try:
            profile = await self.get_profile_by_user_id(user_id)
            if not profile:
                return None

            # Update learning progress if provided
            if 'learning_progress' in profile_data:
                if not profile.learning_progress:
                    profile.learning_progress = LearningProgress(
                        progress_data=str(profile_data['learning_progress']),
                        profile_memory=profile
                    )
                else:
                    profile.learning_progress.progress_data = str(profile_data['learning_progress'])

            # Update preferences if provided
            if 'preferences' in profile_data:
                if not profile.preferences:
                    profile.preferences = UserPreferences(
                        preferences_data=str(profile_data['preferences']),
                        profile_memory=profile
                    )
                else:
                    profile.preferences.preferences_data = str(profile_data['preferences'])

            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error updating profile for user_id {user_id}: {e}")
            await self.session.rollback()
            raise

# Service Class
class ProfileMemoryService:
    """Service class for business logic related to ProfileMemory."""

    def __init__(self, repository: ProfileMemoryRepository):
        self.repository = repository

    async def get_profile(self, user_id: int) -> Optional[ProfileMemory]:
        """Get profile for a given user_id."""
        return await self.repository.get_profile_by_user_id(user_id)

    async def create_profile(self, profile_data: ProfileMemoryCreate) -> ProfileMemory:
        """Create a new profile."""
        if profile_data.user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        return await self.repository.create_profile(profile_data)

    async def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[ProfileMemory]:
        """Update an existing profile."""
        return await self.repository.update_profile(user_id, profile_data)

# Manager Class for easy access
class ProfileMemoryManager:
    """Manager class for ProfileMemory operations."""

    def __init__(self):
        self.service = None

    def _get_service(self, session: AsyncSession):
        """Get or create service instance."""
        if not self.service:
            repository = ProfileMemoryRepository(session)
            self.service = ProfileMemoryService(repository)
        return self.service

    async def get_profile_by_user_id(self, user_id: int, session: AsyncSession) -> Optional[ProfileMemoryOut]:
        """Get profile by user ID."""
        service = self._get_service(session)
        profile = await service.get_profile(user_id)
        if profile:
            return ProfileMemoryOut.from_orm(profile)
        return None

    async def update_profile(self, user_id: int, profile_data: Dict[str, Any], session: AsyncSession) -> Optional[ProfileMemoryOut]:
        """Update user profile."""
        service = self._get_service(session)
        profile = await service.update_profile(user_id, profile_data)
        if profile:
            return ProfileMemoryOut.from_orm(profile)
        return None

    async def create_profile(self, profile_data: ProfileMemoryCreate, session: AsyncSession) -> ProfileMemoryOut:
        """Create new user profile."""
        service = self._get_service(session)
        profile = await service.create_profile(profile_data)
        return ProfileMemoryOut.from_orm(profile) 