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
    BikePricing,
    BikeDocument,
    BikeImage,
    Payment,
    PaymentStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    PlatformSettings,
    AdminAuditLog,
    AuditActorType,
    SupportTicket,
    SupportStatus,
    utcnow,
)
from app.admin.schemas import PlatformSettingsUpdate, AdminDashboardStats
from app.notifications.service import create_notification



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

    owner_user = db.query(User).filter(User.id == owner_id).first()
    if owner_user:
        owner_user.is_verified = approved

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

    if approved:
        create_notification(
            db,
            owner_id,
            "Verification Approved",
            "Congratulations! Your owner verification has been approved.",
        )
    else:
        create_notification(
            db,
            owner_id,
            "Verification Rejected",
            f"Your verification has been rejected. Reason: {owner_profile.rejection_reason}",
        )

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

    driver_user = db.query(User).filter(User.id == driver_id).first()
    if driver_user:
        driver_user.is_verified = approved

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

    if approved:
        create_notification(
            db,
            driver_id,
            "Verification Approved",
            "Congratulations! Your driver verification has been approved.",
        )
    else:
        create_notification(
            db,
            driver_id,
            "Verification Rejected",
            f"Your driver verification has been rejected. Reason: {driver_profile.rejection_reason}",
        )

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

    if approved:
        create_notification(
            db,
            bike.owner_user_id,
            "Bike Approved",
            "Your bike has been approved and is now available for booking.",
        )
    else:
        create_notification(
            db,
            bike.owner_user_id,
            "Bike Rejected",
            f"Your bike verification has been rejected. Reason: {reason or 'Verification rejected by admin.'}",
        )

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

    # Cash on Delivery tracking
    cod_unpaid_count = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
        DriverBikeAssignment.payment_method == "cod",
        DriverBikeAssignment.cash_received == False,
    ).count()

    cod_escalations_count = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
        DriverBikeAssignment.payment_method == "cod",
        DriverBikeAssignment.cash_received == False,
        DriverBikeAssignment.cod_admin_escalated == True,
    ).count()

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
        "cod_unpaid_count": cod_unpaid_count,
        "cod_escalations_count": cod_escalations_count,
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


async def get_all_drivers_service(db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(DriverProfile).join(DriverProfile.user)
    if status:
        query = query.filter(DriverProfile.verification_status == DriverVerificationStatus(status.lower()))
    drivers = query.all()
    res = []
    for d in drivers:
        res.append({
            "user_id": d.user_id,
            "email": d.user.email,
            "phone": d.user.phone,
            "role": d.user.role.value if hasattr(d.user.role, "value") else str(d.user.role),
            "is_active": d.user.is_active,
            "full_name": d.full_name,
            "address": getattr(d, "address", "") or "",
            "driving_license_number": d.driving_license_number,
            "driving_license_file": d.driving_license_file_path,
            "aadhaar_number": d.aadhaar_number,
            "aadhaar_file": d.aadhaar_file_path,
            "pan_number": getattr(d, "pan_number", "") or "",
            "pan_file": getattr(d, "pan_file_path", "") or "",
            "profile_picture": d.profile_picture_path,
            "emergency_contact": {
                "name": d.emergency_contact_name,
                "phone": d.emergency_contact_phone,
            },
            "verification_status": d.verification_status.value if hasattr(d.verification_status, "value") else str(d.verification_status),
            "rejection_reason": d.rejection_reason,
            "reviewed_at": d.reviewed_at.isoformat() if d.reviewed_at else None,
            "created_at": d.created_at.isoformat() if hasattr(d, "created_at") and d.created_at else None,
        })
    return res


async def get_all_owners_service(db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(OwnerProfile).join(OwnerProfile.user)
    if status:
        query = query.filter(OwnerProfile.verification_status == OwnerVerificationStatus(status.lower()))
    owners = query.all()
    res = []
    for o in owners:
        res.append({
            "user_id": o.user_id,
            "email": o.user.email,
            "role": o.user.role.value if hasattr(o.user.role, "value") else str(o.user.role),
            "is_active": o.user.is_active,
            "full_name": o.full_name,
            "phone": o.phone,
            "business_name": o.business_name,
            "profile_picture": o.profile_picture_path,
            "aadhaar_number": o.aadhaar_number,
            "pan_number": o.pan_number,
            "aadhaar_file": o.aadhaar_file_path,
            "pan_file": o.pan_file_path,
            "passbook_file": o.passbook_file_path,
            "bank_account": {
                "name": o.bank_account_name,
                "number": o.bank_account_number,
                "ifsc": o.ifsc_code,
            },
            "address": {
                "line_1": o.address_line_1,
                "line_2": o.address_line_2,
                "city": o.city,
                "state": o.state,
                "postal_code": o.postal_code,
            },
            "verification_status": o.verification_status.value if hasattr(o.verification_status, "value") else str(o.verification_status),
            "rejection_reason": o.rejection_reason,
            "reviewed_at": o.reviewed_at.isoformat() if o.reviewed_at else None,
            "created_at": o.created_at.isoformat() if hasattr(o, "created_at") and o.created_at else None,
        })
    return res


async def get_all_bikes_service(db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(Bike)
    if status:
        query = query.filter(Bike.verification_status == BikeVerificationStatus(status.lower()))
    bikes = query.order_by(Bike.created_at.desc()).all()
    res = []
    for b in bikes:
        docs = b.documents[0] if b.documents else None
        pricing = b.pricing
        images = [img.image_path for img in b.images]
        res.append({
            "id": b.id,
            "owner_user_id": b.owner_user_id,
            "owner_email": b.owner.email if b.owner else None,
            "bike_name": b.bike_name,
            "brand": b.brand,
            "model": b.model,
            "registration_number": b.registration_number,
            "color": b.color,
            "fuel_type": b.fuel_type.value if hasattr(b.fuel_type, "value") else str(b.fuel_type),
            "ownership_type": b.ownership_type.value if hasattr(b.ownership_type, "value") else str(b.ownership_type),
            "km_driven": b.km_driven,
            "year_of_purchase": b.year_of_purchase,
            "status": b.status.value if hasattr(b.status, "value") else str(b.status),
            "verification_status": b.verification_status.value if hasattr(b.verification_status, "value") else str(b.verification_status),
            "is_active": b.is_active,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "pricing": {
                "daily_rent": float(pricing.daily_rent) if pricing else 0.0,
                "weekly_rent": float(pricing.weekly_rent) if pricing and pricing.weekly_rent else None,
                "monthly_rent": float(pricing.monthly_rent) if pricing and pricing.monthly_rent else None,
                "security_deposit": float(pricing.security_deposit) if pricing else 0.0,
                "late_fee_per_day": float(pricing.late_fee_per_day) if pricing else 0.0,
            } if pricing else None,
            "documents": {
                "rc": docs.rc_file_path if docs else None,
                "insurance": docs.insurance_file_path if docs else None,
                "pollution": docs.pollution_file_path if docs else None,
                "permit": docs.permit_file_path if docs else None,
            } if docs else None,
            "images": images,
        })
    return res


async def get_all_users_service(db: Session, role: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == UserRole(role.lower()))
    if status:
        query = query.filter(User.lifecycle_status == UserLifecycleStatus(status.lower()))
    users = query.order_by(User.created_at.desc()).all()
    res = []
    for u in users:
        res.append({
            "id": u.id,
            "email": u.email,
            "phone": u.phone,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "lifecycle_status": u.lifecycle_status.value if hasattr(u.lifecycle_status, "value") else str(u.lifecycle_status),
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "wallet_balance": float(u.wallet.balance) if u.wallet else 0.0,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return res
