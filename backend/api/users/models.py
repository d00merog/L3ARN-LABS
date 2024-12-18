from sqlalchemy import Column, Integer, String, Boolean, ARRAY, JSON
from ...core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    web3_address = Column(String, unique=True, index=True)
    interests = Column(String)
    completed_lessons = Column(ARRAY(Integer), default=[])
    is_active = Column(Boolean, default=True)
    is_instructor = Column(Boolean, default=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    achievements = Column(JSON, default=[])
