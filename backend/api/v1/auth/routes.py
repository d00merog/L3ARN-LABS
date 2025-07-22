from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_async_db
from .....apps.backend.api.auth import schemas
from .crud import create_tokens, rotate_refresh_token, get_current_user
from ..users import crud as user_crud
from .web3 import generate_nonce, verify_signature

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    user = await user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = await create_tokens(db, user)
    return tokens


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    payload: schemas.TokenRefresh,
    db: AsyncSession = Depends(get_async_db),
):
    return await rotate_refresh_token(payload.refresh_token, db)

@router.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await user_crud.create_user(db=db, user=user)
    return await create_tokens(db, new_user)

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
    user = await user_crud.get_user_by_address(db, auth_data.address)
    if not user:
        user = await user_crud.create_user_from_address(db, auth_data.address)
    
    tokens = await create_tokens(db, user)
    return tokens
