from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ...core.database import Base

achievement_user = Table('achievement_user', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('achievement_id', Integer, ForeignKey('achievements.id'))
)

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    icon = Column(String)

    users = relationship("User", secondary=achievement_user, back_populates="achievements")
