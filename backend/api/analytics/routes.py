from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_async_db
from ..auth import crud as auth_crud
from . import schemas, crud

router = APIRouter()

@router.get("/courses/{course_id}/analytics", response_model=schemas.CourseAnalytics)
async def get_course_analytics(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    if not current_user.is_instructor:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    return await crud.get_course_analytics(db, course_id)

@router.get("/instructor/analytics", response_model=List[schemas.LessonAnalytics])
async def get_instructor_analytics(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    if not current_user.is_instructor:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    return await crud.get_instructor_analytics(db, current_user.id)
