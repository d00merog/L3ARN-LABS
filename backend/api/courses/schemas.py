from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: str
    type: str
    topic: str
    difficulty: Optional[str] = None
    era: Optional[str] = None
    model: str

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CourseProgress(BaseModel):
    course_id: int
    progress: float

class LessonBase(BaseModel):
    title: str
    content: str

class LessonCreate(LessonBase):
    course_id: int

class Lesson(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    course_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Enrollment(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        orm_mode = True
