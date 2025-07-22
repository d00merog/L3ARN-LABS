"""
Unified Course CRUD operations with consistent patterns and error handling
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


class CourseCRUD:
    """Unified Course CRUD operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_course(self, course_id: int) -> Optional[models.Course]:
        """Get course by ID with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.Course).where(models.Course.id == course_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting course {course_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_courses(self, skip: int = 0, limit: int = 100) -> List[models.Course]:
        """Get courses with pagination and comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.Course).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting courses: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_courses_by_instructor(self, instructor_id: int) -> List[models.Course]:
        """Get courses by instructor with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.Course).where(models.Course.instructor_id == instructor_id)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting courses by instructor {instructor_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def create_course(self, course_data: Dict[str, Any]) -> models.Course:
        """Create course with comprehensive error handling"""
        try:
            course = models.Course(**course_data)
            self.db.add(course)
            await self.db.commit()
            await self.db.refresh(course)
            logger.info(f"Created course {course.title}")
            return course
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating course: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Optional[models.Course]:
        """Update course with comprehensive error handling"""
        try:
            result = await self.db.execute(
                update(models.Course)
                .where(models.Course.id == course_id)
                .values(**course_data)
            )
            await self.db.commit()
            
            if result.rowcount == 0:
                return None
                
            return await self.get_course(course_id)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating course {course_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def delete_course(self, course_id: int) -> bool:
        """Delete course with comprehensive error handling"""
        try:
            result = await self.db.execute(
                delete(models.Course).where(models.Course.id == course_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting course {course_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_lesson(self, lesson_id: int) -> Optional[models.Lesson]:
        """Get lesson by ID with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.Lesson).where(models.Lesson.id == lesson_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_course_lessons(self, course_id: int) -> List[models.Lesson]:
        """Get lessons for a course with comprehensive error handling"""
        try:
            result = await self.db.execute(
                select(models.Lesson)
                .where(models.Lesson.course_id == course_id)
                .order_by(models.Lesson.order)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting lessons for course {course_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def create_lesson(self, lesson_data: Dict[str, Any]) -> models.Lesson:
        """Create lesson with comprehensive error handling"""
        try:
            lesson = models.Lesson(**lesson_data)
            self.db.add(lesson)
            await self.db.commit()
            await self.db.refresh(lesson)
            logger.info(f"Created lesson {lesson.title}")
            return lesson
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating lesson: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_lesson(self, lesson_id: int, lesson_data: Dict[str, Any]) -> Optional[models.Lesson]:
        """Update lesson with comprehensive error handling"""
        try:
            result = await self.db.execute(
                update(models.Lesson)
                .where(models.Lesson.id == lesson_id)
                .values(**lesson_data)
            )
            await self.db.commit()
            
            if result.rowcount == 0:
                return None
                
            return await self.get_lesson(lesson_id)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def delete_lesson(self, lesson_id: int) -> bool:
        """Delete lesson with comprehensive error handling"""
        try:
            result = await self.db.execute(
                delete(models.Lesson).where(models.Lesson.id == lesson_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error deleting lesson {lesson_id}: {e}")
            raise HTTPException(status_code=500, detail="Database error")


# Dependency function for CRUD operations
async def get_course_crud(db: AsyncSession = Depends(get_async_db)) -> CourseCRUD:
    """Dependency to get CourseCRUD instance"""
    return CourseCRUD(db)
