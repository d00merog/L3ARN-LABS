from sqlalchemy.orm import Session
from . import models, schemas

def get_user_achievements(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.achievements

def award_achievement(db: Session, user_id: int, achievement_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    achievement = db.query(models.Achievement).filter(models.Achievement.id == achievement_id).first()
    if achievement not in user.achievements:
        user.achievements.append(achievement)
        db.commit()
    return achievement
