from pydantic import BaseModel, EmailStr
from typing import Optional, List
from ..courses.schemas import Course

# ... (existing code)

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_instructor: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    is_instructor: bool

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class UserDashboard(BaseModel):
    enrolled_courses: List[Course]
    recommended_courses: List[Course]
