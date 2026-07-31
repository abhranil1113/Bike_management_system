# app/notifications/router.py

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_user, get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.notifications.schemas import BroadcastNotificationRequest
from app.notifications.service import (
    broadcast_notification_service,
    get_user_notifications_service,
    get_unread_count_service,
    mark_notification_read_service,
    mark_all_notifications_read_service,
    delete_notification_service,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=StandardResponse, summary="List User Notifications")
@router.get("/", response_model=StandardResponse, summary="List User Notifications")
@router.get("/me", response_model=StandardResponse, summary="List User Notifications (Me Alias)")
async def get_my_notifications_api(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = get_user_notifications_service(db, user.id, page=page, limit=limit)
    return StandardResponse(
        success=True, message="Notifications fetched successfully.", data=data
    )


@router.get("/unread-count", response_model=StandardResponse, summary="Get Unread Notification Count")
async def get_unread_count_api(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = get_unread_count_service(db, user.id)
    return StandardResponse(
        success=True, message="Unread count fetched.", data={"unread_count": count}
    )


@router.patch("/read-all", response_model=StandardResponse, summary="Mark All Notifications as Read")
async def mark_all_read_api(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    res = mark_all_notifications_read_service(db, user.id)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.patch("/{notification_id}/read", response_model=StandardResponse, summary="Mark Single Notification as Read")
@router.post("/{notification_id}/read", response_model=StandardResponse, summary="Mark Single Notification as Read (Post Alias)")
async def read_notification_api(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    res = mark_notification_read_service(db, user.id, notification_id)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.delete("/{notification_id}", response_model=StandardResponse, summary="Delete Notification")
async def delete_notification_api(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    res = delete_notification_service(db, user.id, notification_id)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/broadcast", response_model=StandardResponse, summary="Admin Broadcast Notification to Users")
async def broadcast_notification_api(
    req: BroadcastNotificationRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    res = await broadcast_notification_service(db, req)
    return StandardResponse(success=True, message=res["message"])
