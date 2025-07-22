from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ...core.database import get_async_db
from ..auth import crud as auth_crud
from ..courses import models as course_models
from ..users import schemas as user_schemas
from ...teacher_agents.history_agent import HistoryTeacher
from ...teacher_agents.math_agent import MathTeacher
from . import schemas, crud

router = APIRouter()

history_teacher = HistoryTeacher(model="gpt-3.5-turbo")
math_teacher = MathTeacher(model="gpt-3.5-turbo")

async def _get_lesson_course(db: AsyncSession, lesson_id: int):
    lesson_res = await db.execute(select(course_models.Lesson).filter(course_models.Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course_res = await db.execute(select(course_models.Course).filter(course_models.Course.id == lesson.course_id))
    course = course_res.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return lesson, course

@router.post("/generate")
async def generate_quiz(
    payload: schemas.QuizGenerateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: user_schemas.User = Depends(auth_crud.get_current_user),
):
    lesson, course = await _get_lesson_course(db, payload.lesson_id)
    if course.type == "history":
        quiz = await history_teacher.generate_quiz(lesson.content)
    elif course.type == "math":
        quiz = await math_teacher.generate_quiz(lesson.content)
    else:
        raise HTTPException(status_code=400, detail="Quiz generation not supported for this course")
    return {"quiz": quiz}

@router.post("/submit", response_model=schemas.QuizResult)
async def submit_quiz(
    submission: schemas.QuizSubmission,
    db: AsyncSession = Depends(get_async_db),
    current_user: user_schemas.User = Depends(auth_crud.get_current_user),
):
    lesson, course = await _get_lesson_course(db, submission.lesson_id)
    if course.type == "history":
        teacher = history_teacher
    elif course.type == "math":
        teacher = math_teacher
    else:
        raise HTTPException(status_code=400, detail="Quiz grading not supported for this course")

    total = len(submission.answers)
    correct = 0
    for ans in submission.answers:
        grade = await teacher.grade_answer(ans.question, ans.student_answer, ans.correct_answer)
        if grade >= 1:
            correct += 1
    score = int((correct / total) * 100) if total else 0
    result = await crud.create_quiz_result(db, current_user.id, submission.lesson_id, score, [a.dict() for a in submission.answers])
    return result

@router.get("/{lesson_id}/results", response_model=List[schemas.QuizResult])
async def get_results(
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: user_schemas.User = Depends(auth_crud.get_current_user),
):
    results = await crud.get_results_by_lesson(db, lesson_id)
    return results
