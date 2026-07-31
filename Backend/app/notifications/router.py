# app/notifications/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, UserNotification
from app.api.deps import get_current_user, get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.notifications.schemas import BroadcastNotificationRequest
from app.notifications.service import (
    broadcast_notification_service,
    mark_notification_read_service,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=StandardResponse, summary="Get User Notifications")
async def get_my_notifications_api(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = db.query(UserNotification).filter(
        UserNotification.user_id == user.id
    ).order_by(UserNotification.created_at.desc()).all()

    unread_count = sum(1 for n in notifs if n.read_at is None)

    data = {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifs
        ],
    }
    return StandardResponse(success=True, message="Notifications fetched.", data=data)


@router.post("/{notification_id}/read", response_model=StandardResponse, summary="Mark Notification as Read")
async def read_notification_api(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = await mark_notification_read_service(db, user.id, notification_id)
    return StandardResponse(success=True, message=res["message"])


@router.post("/broadcast", response_model=StandardResponse, summary="Admin Broadcast Notification to Users")
async def broadcast_notification_api(
    req: BroadcastNotificationRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await broadcast_notification_service(db, req)
    return StandardResponse(success=True, message=res["message"])
