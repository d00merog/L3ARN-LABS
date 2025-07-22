from pydantic import BaseModel
from typing import List
from datetime import datetime

class QuizGenerateRequest(BaseModel):
    lesson_id: int

class QuizAnswer(BaseModel):
    question: str
    student_answer: str
    correct_answer: str

class QuizSubmission(BaseModel):
    lesson_id: int
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    score: int
    created_at: datetime

    class Config:
        orm_mode = True
