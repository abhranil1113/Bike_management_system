# app/notifications/service.py

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.schema import User, UserNotification, UserRole, utcnow
from app.notifications.schemas import BroadcastNotificationRequest


async def create_user_notification(
    db: Session, user_id: str, title: str, message: str
) -> UserNotification:
    notif = UserNotification(user_id=user_id, title=title, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


async def broadcast_notification_service(
    db: Session, req: BroadcastNotificationRequest
) -> Dict[str, Any]:
    q = db.query(User)
    if req.target_role:
        role_enum = UserRole(req.target_role.lower())
        q = q.filter(User.role == role_enum)

    users = q.all()
    count = 0
    for u in users:
        n = UserNotification(user_id=u.id, title=req.title, message=req.message)
        db.add(n)
        count += 1

    db.commit()
    return {"message": f"Broadcast notification sent to {count} users."}


async def mark_notification_read_service(
    db: Session, user_id: str, notification_id: str
) -> Dict[str, Any]:
    notif = db.query(UserNotification).filter(
        UserNotification.id == notification_id,
        UserNotification.user_id == user_id,
    ).first()

    if notif:
        notif.read_at = utcnow()
        db.commit()
    return {"message": "Notification marked as read."}
