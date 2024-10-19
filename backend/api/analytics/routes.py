from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ..auth.crud import get_current_user
from . import schemas, crud

router = APIRouter()

@router.get("/courses/{course_id}/analytics", response_model=schemas.CourseAnalytics)
async def get_course_analytics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not current_user.is_instructor:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    return crud.get_course_analytics(db, course_id)

@router.get("/instructor/analytics", response_model=schemas.InstructorAnalytics)
async def get_instructor_analytics(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not current_user.is_instructor:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")
    return crud.get_instructor_analytics(db, current_user.id)
