from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..users import models, schemas
from ...core.security import verify_password, create_access_token
from datetime import timedelta
from ...core.config.settings import settings

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

def create_user_token(user: schemas.User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
