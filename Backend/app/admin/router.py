# app/admin/router.py

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import (
    User,
    AdminAuditLog,
    DriverBikeAssignment,
    AssignmentStatus,
    DriverProfile,
    OwnerProfile,
    utcnow,
)
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
    get_all_drivers_service,
    get_all_owners_service,
    get_all_bikes_service,
    get_all_users_service,
)

router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.get("/stats", response_model=StandardResponse, summary="Get Admin Dashboard Statistics")
@router.get("/dashboard", response_model=StandardResponse, summary="Get Admin Dashboard Statistics")
async def get_dashboard_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    stats = await get_admin_dashboard_stats(db)
    return StandardResponse(success=True, message="Dashboard stats retrieved.", data=stats)


@router.post("/verify-owner/{owner_id}", response_model=StandardResponse, summary="Approve or Reject Owner Verification")
@router.post("/verify/owner/{owner_id}", response_model=StandardResponse, summary="Approve or Reject Owner Verification")
async def verify_owner_api(
    owner_id: str,
    req: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    approved = req.get("approved", True) if "approved" in req else (req.get("status") == "verified")
    reason = req.get("rejection_reason") or req.get("reason")
    res = await review_owner_verification(db, admin.id, owner_id, approved, reason)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/verify-driver/{driver_id}", response_model=StandardResponse, summary="Approve or Reject Driver Verification")
@router.post("/verify/driver/{driver_id}", response_model=StandardResponse, summary="Approve or Reject Driver Verification")
async def verify_driver_api(
    driver_id: str,
    req: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    approved = req.get("approved", True) if "approved" in req else (req.get("status") == "verified")
    reason = req.get("rejection_reason") or req.get("reason")
    res = await review_driver_verification(db, admin.id, driver_id, approved, reason)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/verify-bike/{bike_id}", response_model=StandardResponse, summary="Approve or Reject Bike Listing")
@router.post("/verify/bike/{bike_id}", response_model=StandardResponse, summary="Approve or Reject Bike Listing")
async def verify_bike_api(
    bike_id: str,
    req: Dict[str, Any] = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    approved = req.get("approved", True) if "approved" in req else (req.get("status") == "verified")
    reason = req.get("rejection_reason") or req.get("reason")
    res = await review_bike_verification(db, admin.id, bike_id, approved, reason)
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


@router.get("/drivers", response_model=StandardResponse, summary="List All Drivers for Admin Verification & Monitoring")
async def get_drivers_api(
    status: Optional[str] = Query(None, description="draft, pending, verified, rejected"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    drivers = await get_all_drivers_service(db, status=status)
    return StandardResponse(success=True, message=f"Fetched {len(drivers)} drivers.", data=drivers)


@router.get("/owners", response_model=StandardResponse, summary="List All Owners for Admin Verification & Monitoring")
async def get_owners_api(
    status: Optional[str] = Query(None, description="draft, pending, verified, rejected"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    owners = await get_all_owners_service(db, status=status)
    return StandardResponse(success=True, message=f"Fetched {len(owners)} owners.", data=owners)


@router.get("/bikes", response_model=StandardResponse, summary="List All Bikes/Scooties for Admin Verification Queue")
async def get_bikes_api(
    status: Optional[str] = Query(None, description="draft, pending, verified, rejected"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    bikes = await get_all_bikes_service(db, status=status)
    return StandardResponse(success=True, message=f"Fetched {len(bikes)} bikes.", data=bikes)


@router.get("/users", response_model=StandardResponse, summary="List All Registered Users")
async def get_users_api(
    role: Optional[str] = Query(None, description="driver, owner, admin"),
    status: Optional[str] = Query(None, description="active, blocked, deleted"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    users = await get_all_users_service(db, role=role, status=status)
    return StandardResponse(success=True, message=f"Fetched {len(users)} users.", data=users)


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


@router.get("/cod-escalations", response_model=StandardResponse, summary="List COD Rentals Pending > 10 Hours or Escalated")
async def get_cod_escalations_api(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    now = utcnow()
    assignments = (
        db.query(DriverBikeAssignment)
        .filter(
            DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
            DriverBikeAssignment.payment_method == "cod",
            DriverBikeAssignment.cash_received == False,
        )
        .order_by(DriverBikeAssignment.assigned_at.asc())
        .all()
    )

    data = []
    for a in assignments:
        elapsed_seconds = (now - a.assigned_at).total_seconds()
        elapsed_hours = int(elapsed_seconds // 3600)
        driver_prof = db.query(DriverProfile).filter(DriverProfile.user_id == a.driver_user_id).first()
        owner_prof = db.query(OwnerProfile).filter(OwnerProfile.user_id == a.owner_user_id).first()
        bike = a.bike

        data.append({
            "assignment_id": a.id,
            "bike_name": bike.bike_name if bike else "Scooty",
            "registration_number": bike.registration_number if bike else "N/A",
            "driver_name": driver_prof.full_name if driver_prof else "Driver",
            "driver_email": a.driver.email if a.driver else "",
            "driver_phone": a.driver.phone if a.driver else "",
            "owner_name": owner_prof.full_name if owner_prof else "Owner",
            "owner_email": a.owner.email if a.owner else "",
            "owner_phone": a.owner.phone if a.owner else "",
            "rent_amount": float(a.total_rent_amount or a.daily_rent_amount),
            "rental_hours": getattr(a, "rental_hours", 24) or 24,
            "assigned_at": a.assigned_at.isoformat(),
            "elapsed_hours": elapsed_hours,
            "is_escalated": elapsed_hours >= 10 or getattr(a, "cod_admin_escalated", False),
        })

    return StandardResponse(success=True, message=f"Found {len(data)} uncollected COD rentals.", data=data)
