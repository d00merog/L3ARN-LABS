"""
Authentication schemas for JWT and OAuth2
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for JWT token payload"""
    email: Optional[str] = None
    exp: Optional[int] = None

class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str
