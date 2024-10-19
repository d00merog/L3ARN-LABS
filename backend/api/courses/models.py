from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ...core.database import Base
from datetime import datetime

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    type = Column(String)
    topic = Column(String)
    difficulty = Column(String, nullable=True)
    era = Column(String, nullable=True)
    model = Column(String)
    content = Column(Text)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lessons = relationship("Lesson", back_populates="course")
    instructor = relationship("User", back_populates="courses")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    content = Column(Text)
    order = Column(Integer)
    difficulty = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="lessons")
