"""
User model with SQLAlchemy ORM
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List

from ..database import Base

# Association tables for many-to-many relationships
courses_enrolled = Table(
    "courses_enrolled",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

courses_teaching = Table(
    "courses_teaching",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    courses_enrolled = relationship(
        "Course",
        secondary=courses_enrolled,
        back_populates="students"
    )
    courses_teaching = relationship(
        "Course",
        secondary=courses_teaching,
        back_populates="instructors"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
