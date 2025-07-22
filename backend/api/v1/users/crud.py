"""
Unified User CRUD operations with consistent patterns and error handling
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends

from . import models
from ...core.database import get_async_db

logger = logging.getLogger(__name__)


class UserCRUD:
    """Unified User CRUD operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user(self, user_id: int) -> Optional[models.User]:
        """Get user by ID with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.User).where(models.User.id == user_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_by_email(self, email: str) -> Optional[models.User]:
        """Get user by email with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.User).where(models.User.email == email)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email {email}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_by_username(self, username: str) -> Optional[models.User]:
        """Get user by username with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.User).where(models.User.username == username)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by username {username}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_by_web3_address(self, address: str) -> Optional[models.User]:
        """Get user by Web3 address with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.User).where(models.User.web3_address == address)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by web3 address {address}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """Get users with pagination and comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.User).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting users: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def create_user(self, user_data: Dict[str, Any]) -> models.User:
        """Create user with comprehensive error handling"""
        try:
            user = models.User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Created user {user.email}")
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating user: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[models.User]:
        """Update user with comprehensive error handling"""
        try:
            result = await self.db.execute(
                update(models.User)
                .where(models.User.id == user_id)
                .values(**user_data)
            )
            await self.db.commit()
            
            if result.rowcount == 0:
                return None
                
            return await self.get_user(user_id)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user with comprehensive error handling"""
        try:
            result = await self.db.execute(
                delete(models.User).where(models.User.id == user_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_course_progress(self, user_id: int) -> List[Dict[str, float]]:
        """Get user course progress with comprehensive error handling"""
        try:
            # This would need to be implemented based on your progress tracking model
            # For now, returning empty list as placeholder
            return []
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user course progress {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user profile with comprehensive error handling"""
        try:
            user = await self.get_user(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "level": user.level,
                "xp": user.xp,
                "achievements": user.achievements,
                "preferences": user.preferences,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Dependency function for CRUD operations
async def get_user_crud(db: AsyncSession = Depends(get_async_db)) -> UserCRUD:
    """Dependency to get UserCRUD instance"""
    return UserCRUD(db)
