"""
Course Pydantic schemas for request/response models
"""
from pydantic import BaseModel, constr, confloat
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CourseLevel(str, Enum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CourseBase(BaseModel):
    """Base course schema with common attributes"""
    title: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    level: CourseLevel = CourseLevel.BEGINNER
    price: confloat(ge=0)

class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    pass

class CourseUpdate(BaseModel):
    """Schema for updating course details"""
    title: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    level: Optional[CourseLevel] = None
    price: Optional[confloat(ge=0)] = None

class CourseInDB(CourseBase):
    """Schema for course in database"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseList(BaseModel):
    """Schema for course list response"""
    id: int
    title: str
    level: CourseLevel
    price: float

    class Config:
        from_attributes = True

class CourseDetail(CourseInDB):
    """Schema for detailed course response"""
    students: List["UserList"] = []
    instructors: List["UserList"] = []

    class Config:
        from_attributes = True
