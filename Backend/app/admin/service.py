# app/admin/service.py

from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.db.schema import (
    User,
    UserRole,
    UserLifecycleStatus,
    OwnerProfile,
    OwnerVerificationStatus,
    DriverProfile,
    DriverVerificationStatus,
    Bike,
    BikeStatus,
    BikeVerificationStatus,
    Payment,
    PaymentStatus,
    PlatformSettings,
    AdminAuditLog,
    AuditActorType,
    SupportTicket,
    SupportStatus,
    utcnow,
)
from app.admin.schemas import PlatformSettingsUpdate, AdminDashboardStats


# ============================================================
# VERIFICATION SERVICES
# ============================================================

async def review_owner_verification(
    db: Session, admin_id: str, owner_id: str, approved: bool, reason: Optional[str] = None
) -> Dict[str, Any]:
    owner_profile = db.query(OwnerProfile).filter(OwnerProfile.user_id == owner_id).first()
    if not owner_profile:
        raise HTTPException(status_code=404, detail="Owner profile not found")

    owner_profile.reviewed_by_admin_id = admin_id
    owner_profile.reviewed_at = utcnow()

    if approved:
        owner_profile.verification_status = OwnerVerificationStatus.VERIFIED
        owner_profile.rejection_reason = None
        msg = "Owner verified successfully."
    else:
        owner_profile.verification_status = OwnerVerificationStatus.REJECTED
        owner_profile.rejection_reason = reason or "Verification rejected by admin."
        msg = "Owner verification rejected."

    # Audit log
    audit = AdminAuditLog(
        actor_user_id=admin_id,
        actor_type=AuditActorType.ADMIN,
        action="REVIEW_OWNER_VERIFICATION",
        entity_type="owner_profiles",
        entity_id=owner_profile.id,
        after_json=f'{{"status": "{owner_profile.verification_status.value}"}}',
    )
    db.add(audit)
    db.commit()
    db.refresh(owner_profile)

    return {"message": msg, "verification_status": owner_profile.verification_status.value}


async def review_driver_verification(
    db: Session, admin_id: str, driver_id: str, approved: bool, reason: Optional[str] = None
) -> Dict[str, Any]:
    driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == driver_id).first()
    if not driver_profile:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    driver_profile.reviewed_at = utcnow()

    if approved:
        driver_profile.verification_status = DriverVerificationStatus.VERIFIED
        driver_profile.rejection_reason = None
        msg = "Driver verified successfully."
    else:
        driver_profile.verification_status = DriverVerificationStatus.REJECTED
        driver_profile.rejection_reason = reason or "Verification rejected by admin."
        msg = "Driver verification rejected."

    audit = AdminAuditLog(
        actor_user_id=admin_id,
        actor_type=AuditActorType.ADMIN,
        action="REVIEW_DRIVER_VERIFICATION",
        entity_type="driver_profiles",
        entity_id=driver_profile.id,
        after_json=f'{{"status": "{driver_profile.verification_status.value}"}}',
    )
    db.add(audit)
    db.commit()
    db.refresh(driver_profile)

    return {"message": msg, "verification_status": driver_profile.verification_status.value}


async def review_bike_verification(
    db: Session, admin_id: str, bike_id: str, approved: bool, reason: Optional[str] = None
) -> Dict[str, Any]:
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    if approved:
        bike.verification_status = BikeVerificationStatus.VERIFIED
        bike.status = BikeStatus.AVAILABLE
        msg = "Bike verified and published."
    else:
        bike.verification_status = BikeVerificationStatus.REJECTED
        bike.status = BikeStatus.INACTIVE
        msg = "Bike verification rejected."

    audit = AdminAuditLog(
        actor_user_id=admin_id,
        actor_type=AuditActorType.ADMIN,
        action="REVIEW_BIKE_VERIFICATION",
        entity_type="bikes",
        entity_id=bike.id,
        after_json=f'{{"verification_status": "{bike.verification_status.value}", "status": "{bike.status.value}"}}',
    )
    db.add(audit)
    db.commit()
    db.refresh(bike)

    return {"message": msg, "verification_status": bike.verification_status.value}


# ============================================================
# USER MANAGEMENT & BLOCK/UNBLOCK
# ============================================================

async def set_user_status(
    db: Session, admin_id: str, target_user_id: str, status_str: str
) -> Dict[str, Any]:
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    status_str_lower = status_str.lower()
    if status_str_lower == "active":
        target_user.lifecycle_status = UserLifecycleStatus.ACTIVE
        target_user.is_active = True
    elif status_str_lower == "blocked":
        target_user.lifecycle_status = UserLifecycleStatus.BLOCKED
        target_user.is_active = False
    elif status_str_lower == "deleted":
        target_user.lifecycle_status = UserLifecycleStatus.DELETED
        target_user.is_active = False
    else:
        raise HTTPException(status_code=400, detail="Invalid lifecycle status")

    audit = AdminAuditLog(
        actor_user_id=admin_id,
        actor_type=AuditActorType.ADMIN,
        action=f"SET_USER_STATUS_{status_str.upper()}",
        entity_type="users",
        entity_id=target_user.id,
    )
    db.add(audit)
    db.commit()
    db.refresh(target_user)

    return {"message": f"User status updated to {target_user.lifecycle_status.value}."}


# ============================================================
# PLATFORM SETTINGS & DASHBOARD
# ============================================================

async def get_admin_dashboard_stats(db: Session) -> Dict[str, Any]:
    total_users = db.query(User).count()
    total_owners = db.query(User).filter(User.role == UserRole.OWNER).count()
    total_drivers = db.query(User).filter(User.role == UserRole.DRIVER).count()

    total_bikes = db.query(Bike).count()
    available_bikes = db.query(Bike).filter(Bike.status == BikeStatus.AVAILABLE).count()
    assigned_bikes = db.query(Bike).filter(Bike.status == BikeStatus.ASSIGNED).count()

    pending_owners = db.query(OwnerProfile).filter(OwnerProfile.verification_status == OwnerVerificationStatus.PENDING).count()
    pending_drivers = db.query(DriverProfile).filter(DriverProfile.verification_status == DriverVerificationStatus.PENDING).count()
    pending_bikes = db.query(Bike).filter(Bike.verification_status == BikeVerificationStatus.PENDING).count()

    tot_payments = db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.SUCCESS).scalar() or Decimal("0.00")

    settings = db.query(PlatformSettings).first()
    commission_pct = settings.platform_commission_percent if settings else Decimal("10.00")
    tot_commission = (tot_payments * commission_pct) / Decimal("100.00")

    return {
        "total_users": total_users,
        "total_owners": total_owners,
        "total_drivers": total_drivers,
        "total_bikes": total_bikes,
        "available_bikes": available_bikes,
        "assigned_bikes": assigned_bikes,
        "pending_owner_verifications": pending_owners,
        "pending_driver_verifications": pending_drivers,
        "pending_bike_verifications": pending_bikes,
        "total_revenue": float(tot_payments),
        "total_platform_commission": float(tot_commission),
    }


async def update_platform_settings(db: Session, admin_id: str, req: PlatformSettingsUpdate) -> Dict[str, Any]:
    plat_settings = db.query(PlatformSettings).first()
    if not plat_settings:
        plat_settings = PlatformSettings()
        db.add(plat_settings)

    plat_settings.platform_commission_percent = req.platform_commission_percent
    plat_settings.late_fee_grace_days = req.late_fee_grace_days

    audit = AdminAuditLog(
        actor_user_id=admin_id,
        actor_type=AuditActorType.ADMIN,
        action="UPDATE_PLATFORM_SETTINGS",
        entity_type="platform_settings",
        entity_id=plat_settings.id,
    )
    db.add(audit)
    db.commit()

    return {"message": "Platform settings updated successfully."}
