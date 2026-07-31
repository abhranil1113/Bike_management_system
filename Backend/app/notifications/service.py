# app/notifications/service.py

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.schema import User, UserNotification, UserRole, utcnow
from app.notifications.schemas import BroadcastNotificationRequest


def create_notification(
    db: Session, user_id: str, title: str, message: str
) -> UserNotification:
    """
    Reusable helper to create and save a UserNotification record.
    Also dispatches real-time notification to socket if active.
    """
    notif = UserNotification(user_id=user_id, title=title, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Real-time WebSocket event emission if socket_manager is active
    try:
        from app.notifications.socket_manager import socket_manager
        socket_manager.notify_user_sync(user_id, {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "read_at": notif.read_at.isoformat() if notif.read_at else None,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        })
    except Exception:
        pass

    return notif


async def create_user_notification(
    db: Session, user_id: str, title: str, message: str
) -> UserNotification:
    """Async alias for create_notification for backward compatibility."""
    return create_notification(db, user_id, title, message)


def get_user_notifications_service(
    db: Session, user_id: str, page: int = 1, limit: int = 10
) -> Dict[str, Any]:
    """
    List all notifications of the logged-in user with pagination.
    Ordered by latest first.
    """
    query = (
        db.query(UserNotification)
        .filter(UserNotification.user_id == user_id)
        .order_by(UserNotification.created_at.desc())
    )
    total = query.count()
    offset = (page - 1) * limit
    notifs = query.offset(offset).limit(limit).all()

    unread_count = (
        db.query(UserNotification)
        .filter(UserNotification.user_id == user_id, UserNotification.read_at.is_(None))
        .count()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ],
    }


def get_unread_count_service(db: Session, user_id: str) -> int:
    """Return unread notification count for user."""
    return (
        db.query(UserNotification)
        .filter(UserNotification.user_id == user_id, UserNotification.read_at.is_(None))
        .count()
    )


def mark_notification_read_service(
    db: Session, user_id: str, notification_id: str
) -> Dict[str, Any]:
    """Mark a single notification of user as read."""
    notif = (
        db.query(UserNotification)
        .filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id,
        )
        .first()
    )

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notif.read_at is None:
        notif.read_at = utcnow()
        db.commit()
        db.refresh(notif)
    return {"message": "Notification marked as read.", "notification_id": notif.id}


def mark_all_notifications_read_service(
    db: Session, user_id: str
) -> Dict[str, Any]:
    """Mark all notifications of logged-in user as read."""
    count = (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.read_at.is_(None),
        )
        .update({UserNotification.read_at: utcnow()}, synchronize_session=False)
    )
    db.commit()
    return {"message": f"Marked {count} notifications as read.", "count": count}


def delete_notification_service(
    db: Session, user_id: str, notification_id: str
) -> Dict[str, Any]:
    """Delete a user notification."""
    notif = (
        db.query(UserNotification)
        .filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id,
        )
        .first()
    )

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted successfully.", "notification_id": notification_id}


def notify_rental_overdue(db: Session, driver_user_id: str) -> UserNotification:
    """Trigger rental payment overdue notification for driver."""
    return create_notification(
        db=db,
        user_id=driver_user_id,
        title="Rental Due",
        message="Your rental payment is overdue.",
    )


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
