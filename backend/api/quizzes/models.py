from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..courses.models import Lesson
from ..users.models import User
from ...core.database import Base

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    question = Column(String)
    given_answer = Column(String)
    is_correct = Column(Boolean, default=False)

    user = relationship(User)
    lesson = relationship(Lesson)
