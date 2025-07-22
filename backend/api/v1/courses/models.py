from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core.database import Base
import enum
from typing import List


class CourseLevel(str, enum.Enum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(Base):
    """Unified Course model for learning content with comprehensive features"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    type = Column(String)
    topic = Column(String)
    level = Column(Enum(CourseLevel), default=CourseLevel.BEGINNER)
    difficulty = Column(String, nullable=True)
    era = Column(String, nullable=True)
    model = Column(String)
    content = Column(Text)
    price = Column(Float, nullable=False, default=0.0)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lessons = relationship("Lesson", back_populates="course")
    instructor = relationship("User", back_populates="courses_teaching")
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

    def __repr__(self) -> str:
        return f"<Course {self.title}>"


class Lesson(Base):
    """Lesson model for course content"""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    content = Column(Text)
    order = Column(Integer)
    difficulty = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    course = relationship("Course", back_populates="lessons")

    def __repr__(self) -> str:
        return f"<Lesson {self.title}>"
