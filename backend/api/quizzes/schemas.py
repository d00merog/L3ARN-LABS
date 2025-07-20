from pydantic import BaseModel
from typing import List

class QuizGenerationRequest(BaseModel):
    lesson_id: int

class QuizQuestionSubmission(BaseModel):
    question: str
    student_answer: str
    correct_answer: str

class QuizSubmission(BaseModel):
    user_id: int
    lesson_id: int
    answers: List[QuizQuestionSubmission]
