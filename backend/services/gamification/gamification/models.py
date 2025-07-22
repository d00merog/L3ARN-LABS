from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ...core.database import Base
from datetime import datetime

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    icon = Column(String)
    xp_reward = Column(Integer)

class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    xp_reward = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    date_earned = Column(DateTime, default=datetime.utcnow)

class UserDailyChallenge(Base):
    __tablename__ = "user_daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id"))
    date_completed = Column(DateTime, default=datetime.utcnow)
