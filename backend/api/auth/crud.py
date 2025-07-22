from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta, datetime
from hashlib import sha256

from ...core.database import get_async_db
from ...core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ..users.models import User
from .models import RefreshToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def create_tokens(db: AsyncSession, user: User):
    access = create_access_token({"sub": user.email, "role": user.role})
    refresh = create_refresh_token({"sub": user.email})
    hashed = sha256(refresh.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=7)
    db_token = RefreshToken(token=hashed, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    await db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "Teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher role required",
        )
    return current_user

async def rotate_refresh_token(
    refresh_token: str,
    db: AsyncSession,
) -> dict:
    hashed = sha256(refresh_token.encode()).hexdigest()
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == hashed))
    stored = result.scalar_one_or_none()
    if not stored or stored.revoked or stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    stored.revoked = True
    new_tokens = await create_tokens(db, stored.user)
    await db.commit()
    return new_tokens
