# Create a new file for notification routes

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_async_db
from . import schemas, crud
from ...api.auth import crud as auth_crud

router = APIRouter()

@router.get("/", response_model=List[schemas.Notification])
async def get_user_notifications(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    notifications = await crud.get_user_notifications(db, user_id=current_user.id)
    return notifications

@router.post("/{notification_id}/read", response_model=schemas.Notification)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    notification = await crud.mark_notification_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
