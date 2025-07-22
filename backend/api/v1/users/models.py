from sqlalchemy import Column, Integer, String, Boolean, ARRAY, JSON, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core.database import Base
import enum
from typing import List


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


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
    """Unified User model for authentication, profile management, and gamification"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    web3_address = Column(String, unique=True, index=True)
    interests = Column(String)
    completed_lessons = Column(ARRAY(Integer), default=[])
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default=UserRole.STUDENT.value, nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    achievements = Column(JSON, default=[])
    preferences = Column(JSON, default={})
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
    subscription = relationship("Subscription", uselist=False, back_populates="user")
    profile_memory = relationship("ProfileMemory", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class ProfileMemory(Base):
    """Profile memory model for storing user profile information"""
    __tablename__ = 'profile_memory'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile_memory")
    learning_progress = relationship("LearningProgress", back_populates="profile_memory", uselist=False)
    preferences = relationship("UserPreferences", back_populates="profile_memory", uselist=False)

    def __repr__(self) -> str:
        return f"<ProfileMemory {self.user_id}>"


class LearningProgress(Base):
    """Learning progress model for storing user's learning progress"""
    __tablename__ = 'learning_progress'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    progress_data = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    profile_memory = relationship("ProfileMemory", back_populates="learning_progress")

    def __repr__(self) -> str:
        return f"<LearningProgress {self.profile_memory_id}>"


class UserPreferences(Base):
    """User preferences model for storing user's preferences"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    profile_memory_id = Column(Integer, ForeignKey('profile_memory.id'))
    preferences_data = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    profile_memory = relationship("ProfileMemory", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences {self.profile_memory_id}>"
