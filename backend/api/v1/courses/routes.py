from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_async_db
from . import crud, models, schemas, recommendation
from ..auth import crud as auth_crud
from ...ml.recommendation_model import RecommendationModel
from ...agents.adaptive_quiz_agent import app as adaptive_quiz_app
from ...agents.peer_review_agent import app as peer_review_app

router = APIRouter()
recommendation_model = RecommendationModel()

@router.get("/", response_model=List[schemas.Course])
async def get_courses(
    skip: int = 0,
    limit: int = 10,
    search: str = Query(None, min_length=3, max_length=50),
    course_type: str = Query(None, regex="^(language|history|math)$"),
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    courses = await crud.get_courses(db, skip=skip, limit=limit, search=search, course_type=course_type)
    return courses

@router.post("/", response_model=schemas.Course)
async def create_course(
    course: schemas.CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    return await crud.create_course(db, course=course, user_id=current_user.id)

@router.get("/{course_id}", response_model=schemas.Course)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    course = await crud.get_course(db, course_id=course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=schemas.Course)
async def update_course(
    course_id: int,
    course: schemas.CourseUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    updated_course = await crud.update_course(db, course_id=course_id, course=course, user_id=current_user.id)
    if updated_course is None:
        raise HTTPException(status_code=404, detail="Course not found or you don't have permission to update it")
    return updated_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    deleted = await crud.delete_course(db, course_id=course_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found or you don't have permission to delete it")

@router.get("/recommended", response_model=List[schemas.Course])
async def get_recommended_courses(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user),
    limit: int = Query(5, ge=1, le=20)
):
    courses = await crud.get_recommended_courses(db, user_id=current_user.id, limit=limit)
    return courses

@router.post("/{course_id}/enroll", response_model=schemas.Enrollment)
async def enroll_in_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    enrollment = await crud.enroll_user_in_course(db, user_id=current_user.id, course_id=course_id)
    if not enrollment:
        raise HTTPException(status_code=400, detail="User is already enrolled in this course or the course doesn't exist")
    return enrollment

@router.get("/recommendations/{user_id}")
async def get_course_recommendations(user_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        recommendations = await recommendation_model.get_recommendations(user_id, db)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.post("/quiz/start")
async def start_quiz():
    initial_state = adaptive_quiz_app.invoke({})
    return initial_state

@router.post("/quiz/answer")
async def answer_quiz(state: dict):
    # This is a simplified interaction. In a real application, you would
    # manage the state more carefully.
    next_state = adaptive_quiz_app.invoke(state)
    return next_state

@router.post("/peer_review/submit")
async def submit_for_peer_review(submission: dict):
    initial_state = peer_review_app.invoke(submission)
    return initial_state
