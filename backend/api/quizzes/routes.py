from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.database import get_async_db
from ..auth import crud as auth_crud
from ..users.schemas import User
from . import schemas, crud
from ..teacher_agents.history_agent import HistoryTeacher
from ..teacher_agents.math_agent import MathTeacher
from ..teacher_agents.language_agent import LanguageTeacher
from ..teacher_agents.science_agent import ScienceTeacherAgent
from ..teacher_agents.tech_agent import TechTeacherAgent

router = APIRouter()


def _get_teacher(course_type: str, model_name: str | None = None):
    model = model_name or "gpt-3.5-turbo"
    course_type = (course_type or "").lower()
    if course_type == "history":
        return HistoryTeacher(model)
    if course_type == "math":
        return MathTeacher(model)
    if course_type == "science":
        return ScienceTeacherAgent(model_name=model)
    if course_type in {"tech", "technology"}:
        return TechTeacherAgent(model_name=model)
    if course_type == "language":
        return LanguageTeacher(model)
    return HistoryTeacher(model)


@router.post("/generate")
async def generate_quiz(
    request: schemas.QuizGenerationRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_crud.get_current_user),
):
    lesson, course = await crud.get_lesson_with_course(db, request.lesson_id)
    if not lesson or not course:
        raise HTTPException(status_code=404, detail="Lesson not found")
    teacher = _get_teacher(course.type, course.model)
    quiz = await teacher.generate_quiz(lesson.content)
    return {"quiz": quiz}


@router.post("/submit", response_model=crud.gradebook_schemas.QuizResult)
async def submit_quiz(
    submission: schemas.QuizSubmission,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_crud.get_current_user),
):
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this user")
    lesson, course = await crud.get_lesson_with_course(db, submission.lesson_id)
    if not lesson or not course:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if not submission.answers:
        raise HTTPException(status_code=400, detail="No answers provided")
    correct = 0
    for ans in submission.answers:
        if ans.student_answer.strip().lower() == ans.correct_answer.strip().lower():
            correct += 1
    score = (correct / len(submission.answers)) * 100
    result = await crud.save_quiz_result(db, submission.user_id, submission.lesson_id, score)
    return result


@router.get("/{lesson_id}/results", response_model=List[crud.gradebook_schemas.QuizResult])
async def lesson_results(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
    from ..gradebook import crud as gradebook_crud

    return await gradebook_crud.get_results_by_lesson(db, lesson_id)
