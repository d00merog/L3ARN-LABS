from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.database import get_async_db
from ..auth import crud as auth_crud
from ..users.schemas import User
from . import schemas, crud

router = APIRouter()

@router.post("/results", response_model=schemas.QuizResult)
async def create_result(
    result: schemas.QuizResultCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(auth_crud.get_current_user),
):
    if result.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this user")
    return await crud.create_quiz_result(db, result)

@router.get("/results/user/{user_id}", response_model=List[schemas.QuizResult])
async def results_by_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_results_by_user(db, user_id)

@router.get("/results/lesson/{lesson_id}", response_model=List[schemas.QuizResult])
async def results_by_lesson(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_results_by_lesson(db, lesson_id)
