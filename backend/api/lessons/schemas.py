from pydantic import BaseModel
from typing import Optional

class LessonBase(BaseModel):
    title: str
    content: str
    description: Optional[str] = None
    order: Optional[int] = None
    difficulty: Optional[str] = None
    course_id: int

class LessonCreate(LessonBase):
    pass

class Lesson(LessonBase):
    id: int

    class Config:
        orm_mode = True
