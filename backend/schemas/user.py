"""
User Pydantic schemas for request/response models
"""
from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: constr(min_length=8)
    confirm_password: str

    def validate_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

class UserUpdate(BaseModel):
    """Schema for updating user details"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None

class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserList(BaseModel):
    """Schema for user list response"""
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserDetail(UserInDB):
    """Schema for detailed user response"""
    courses_enrolled: List["CourseList"] = []
    courses_teaching: List["CourseList"] = []

    class Config:
        from_attributes = True
