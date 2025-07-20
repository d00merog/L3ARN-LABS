from datetime import datetime, timedelta
from authlib.jose import jwt, JoseError
from passlib.context import CryptContext
from ..core.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = int((datetime.utcnow() + expires_delta).timestamp())
    header = {"alg": settings.ALGORITHM}
    return jwt.encode(header, payload, settings.SECRET_KEY)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    expires_delta = expires_delta or timedelta(minutes=15)
    return _create_token(data, expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    expires_delta = expires_delta or timedelta(days=7)
    return _create_token(data, expires_delta)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY)
    except JoseError:
        return None
