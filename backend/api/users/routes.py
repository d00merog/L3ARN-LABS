from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_async_db
from . import schemas, crud
from ..auth.crud import get_current_user
from ..courses import schemas as course_schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: AsyncSession = Depends(get_async_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await crud.update_user(db, db_user, user)

@router.get("/me/dashboard", response_model=schemas.UserDashboard)
async def get_user_dashboard(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(get_current_user)
):
    enrolled_courses = await crud.get_user_enrolled_courses(db, user_id=current_user.id)
    recommended_courses = await crud.get_recommended_courses(db, user_id=current_user.id)
    return schemas.UserDashboard(
        enrolled_courses=enrolled_courses,
        recommended_courses=recommended_courses
    )

@router.get("/me/progress", response_model=List[course_schemas.CourseProgress])
async def get_user_progress(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(get_current_user)
):
    progress = await crud.get_user_course_progress(db, user_id=current_user.id)
    return progress
