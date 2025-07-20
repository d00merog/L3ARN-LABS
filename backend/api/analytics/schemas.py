from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LessonAnalytics(BaseModel):
    lesson_id: int
    lesson_title: str
    avg_score: float
    attempts: int
    last_activity: Optional[datetime]

    class Config:
        orm_mode = True

class InstructorAnalytics(BaseModel):
    lessons: List[LessonAnalytics]

class CourseAnalytics(BaseModel):
    course_id: int
    avg_score: float
    attempts: int
