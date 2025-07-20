from pydantic import BaseModel
from datetime import datetime

class QuizResultBase(BaseModel):
    user_id: int
    lesson_id: int
    score: float

class QuizResultCreate(QuizResultBase):
    pass

class QuizResult(QuizResultBase):
    id: int
    taken_at: datetime

    class Config:
        orm_mode = True
