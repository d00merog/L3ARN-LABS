from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

def create_course_update_notification(db: Session, course_id: int, message: str):
    enrolled_users = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()
    notifications = []
    for enrollment in enrolled_users:
        notification = models.Notification(
            user_id=enrollment.user_id,
            message=message,
            notification_type="course_update"
        )
        db.add(notification)
        notifications.append(notification)
    db.commit()
    return notifications

def create_deadline_notification(db: Session, course_id: int, deadline: datetime, message: str):
    enrolled_users = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()
    notifications = []
    for enrollment in enrolled_users:
        notification = models.Notification(
            user_id=enrollment.user_id,
            message=message,
            notification_type="deadline",
            due_date=deadline
        )
        db.add(notification)
        notifications.append(notification)
    db.commit()
    return notifications

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
    return notification
