# app/admin/router.py

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, AdminAuditLog
from app.api.deps import get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.admin.schemas import ApprovalDecisionRequest, UserStatusUpdateRequest, PlatformSettingsUpdate
from app.admin.service import (
    review_owner_verification,
    review_driver_verification,
    review_bike_verification,
    set_user_status,
    get_admin_dashboard_stats,
    update_platform_settings,
)

router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.get("/dashboard", response_model=StandardResponse, summary="Get Admin Dashboard Statistics")
async def get_dashboard_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    stats = await get_admin_dashboard_stats(db)
    return StandardResponse(success=True, message="Dashboard stats retrieved.", data=stats)


@router.post("/verify-owner/{owner_id}", response_model=StandardResponse, summary="Approve or Reject Owner Verification")
async def verify_owner_api(
    owner_id: str,
    req: ApprovalDecisionRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await review_owner_verification(db, admin.id, owner_id, req.approved, req.rejection_reason)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/verify-driver/{driver_id}", response_model=StandardResponse, summary="Approve or Reject Driver Verification")
async def verify_driver_api(
    driver_id: str,
    req: ApprovalDecisionRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await review_driver_verification(db, admin.id, driver_id, req.approved, req.rejection_reason)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/verify-bike/{bike_id}", response_model=StandardResponse, summary="Approve or Reject Bike Listing")
async def verify_bike_api(
    bike_id: str,
    req: ApprovalDecisionRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await review_bike_verification(db, admin.id, bike_id, req.approved, req.rejection_reason)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/users/{user_id}/status", response_model=StandardResponse, summary="Block, Unblock, or Delete User")
async def user_status_api(
    user_id: str,
    req: UserStatusUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await set_user_status(db, admin.id, user_id, req.status)
    return StandardResponse(success=True, message=res["message"])


@router.post("/settings", response_model=StandardResponse, summary="Update Platform Settings & Commission Rate")
async def update_settings_api(
    req: PlatformSettingsUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await update_platform_settings(db, admin.id, req)
    return StandardResponse(success=True, message=res["message"])


@router.get("/audit-logs", response_model=StandardResponse, summary="View Admin Audit Logs")
async def get_audit_logs_api(
    admin: User = Depends(get_current_admin),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    logs = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit).all()
    logs_data = [
        {
            "id": l.id,
            "actor_user_id": l.actor_user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
    return StandardResponse(success=True, message="Audit logs retrieved.", data=logs_data)
