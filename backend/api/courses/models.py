from sqlalchemy import Column, Integer, String, Text, ForeignKey
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
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    content = Column(String(1000))
    course_id = Column(Integer, ForeignKey('courses.id'))

    course = relationship("Course", back_populates="lessons")