from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Web3AuthRequest(BaseModel):
    address: str
    chain: int
    network: str

class Web3AuthVerify(Web3AuthRequest):
    message: str
    signature: str
