"""
Course model with SQLAlchemy ORM
"""
from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import List

from ..database import Base

class CourseLevel(str, enum.Enum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Course(Base):
    """Course model for learning content"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    level = Column(Enum(CourseLevel), default=CourseLevel.BEGINNER)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    students = relationship(
        "User",
        secondary="courses_enrolled",
        back_populates="courses_enrolled"
    )
    instructors = relationship(
        "User",
        secondary="courses_teaching",
        back_populates="courses_teaching"
    )
    lessons = relationship("Lesson", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course {self.title}>"
