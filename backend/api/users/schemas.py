from pydantic import BaseModel, EmailStr
from typing import Optional, List
from ..courses.schemas import Course

# ... (existing code)

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        orm_mode = True

class UserProfile(User):
    bio: Optional[str] = None
    interests: List[str] = []

class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    interests: Optional[List[str]] = None

class Course(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True

class CourseProgress(BaseModel):
    course_id: int
    course_title: str
    completed_lessons: int
    total_lessons: int

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class UserDashboard(BaseModel):
    enrolled_courses: List[Course]
    recommended_courses: List[Course]
