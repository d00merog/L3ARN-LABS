from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_async_db
from ...core.security import create_access_token
from datetime import timedelta
from ...core.config.settings import settings
from . import schemas
from ..users import crud
from .web3 import generate_nonce, verify_signature

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)

@router.post("/web3nonce")
async def web3_nonce(user_data: schemas.Web3AuthRequest):
    nonce = generate_nonce()
    message = f"Sign this message to authenticate: {nonce}"
    # In a production environment, you should store this nonce associated with the user's address
    return {"message": message}

@router.post("/web3verify")
async def web3_verify(auth_data: schemas.Web3AuthVerify, db: AsyncSession = Depends(get_async_db)):
    if not verify_signature(auth_data.message, auth_data.signature, auth_data.address):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Check if the user exists, if not, create a new user
    user = await crud.get_user_by_address(db, auth_data.address)
    if not user:
        user = await crud.create_user_from_address(db, auth_data.address)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
