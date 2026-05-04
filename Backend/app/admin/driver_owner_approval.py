from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import (
    DriverProfile,
    OwnerProfile,
    DriverVerificationStatus,
    OwnerVerificationStatus,
)
from app.admin.admin_deps import get_current_admin


router = APIRouter(prefix="/admin", tags=["Admin - Driver & Owner"])


# =========================================================
# DRIVER LIST (FULL CLEAN RESPONSE)
# =========================================================

@router.get("/drivers")
def get_all_drivers(
    status: Optional[DriverVerificationStatus] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    query = db.query(DriverProfile).join(DriverProfile.user)

    if status:
        query = query.filter(DriverProfile.verification_status == status)

    drivers = query.all()

    result = []

    for driver in drivers:
        result.append({
            "user_id": driver.user_id,
            "email": driver.user.email,
            "role": driver.user.role,

            "full_name": driver.full_name,
            "driving_license_number": driver.driving_license_number,
            "aadhaar_number": driver.aadhaar_number,

            "emergency_contact": {
                "name": driver.emergency_contact_name,
                "phone": driver.emergency_contact_phone,
            },

            "verification_status": driver.verification_status,
            "rejection_reason": driver.rejection_reason,
            "reviewed_at": driver.reviewed_at,
        })

    return {
        "count": len(result),
        "data": result
    }


# =========================================================
# OWNER LIST (FULL CLEAN RESPONSE)
# =========================================================

@router.get("/owners")
def get_all_owners(
    status: Optional[OwnerVerificationStatus] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    query = db.query(OwnerProfile).join(OwnerProfile.user)

    if status:
        query = query.filter(OwnerProfile.verification_status == status)

    owners = query.all()

    result = []

    for owner in owners:
        result.append({
            "user_id": owner.user_id,
            "email": owner.user.email,
            "role": owner.user.role,

            "full_name": owner.full_name,
            "phone": owner.phone,
            "profile_picture": owner.profile_picture_path,

            "aadhaar_number": owner.aadhaar_number,
            "pan_number": owner.pan_number,

            "aadhaar_file": owner.aadhaar_file_path,
            "pan_file": owner.pan_file_path,
            "passbook_file": owner.passbook_file_path,

            "bank_details": {
                "account_name": owner.bank_account_name,
                "account_number": owner.bank_account_number,
                "ifsc": owner.ifsc_code,
            },

            "address": {
                "line1": owner.address_line_1,
                "line2": owner.address_line_2,
                "city": owner.city,
                "state": owner.state,
                "postal_code": owner.postal_code,
            },

            "verification_status": owner.verification_status,
            "rejection_reason": owner.rejection_reason,
            "reviewed_at": owner.reviewed_at,
        })

    return {
        "count": len(result),
        "data": result
    }


# =========================================================
# DRIVER APPROVAL (FIXED)
# =========================================================

@router.patch("/driver/{driver_id}")
def approve_driver(
    driver_id: str,
    action: Literal["approve", "reject"] = Query(...),
    reason: Optional[str] = Query(None),

    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    driver = db.query(DriverProfile).filter(
        DriverProfile.user_id == driver_id
    ).first()

    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # ❗ Reject must have reason
    if action == "reject" and not reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required"
        )

    # Optional safety
    if driver.verification_status == DriverVerificationStatus.VERIFIED:
        raise HTTPException(400, "Driver already verified")

    if action == "approve":
        driver.verification_status = DriverVerificationStatus.VERIFIED
        driver.rejection_reason = None

    else:
        driver.verification_status = DriverVerificationStatus.REJECTED
        driver.rejection_reason = reason

    driver.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(driver)

    return {
        "message": f"Driver {action}d successfully",
        "driver_id": driver_id
    }


# =========================================================
# OWNER APPROVAL (FIXED)
# =========================================================

@router.patch("/owner/{owner_id}")
def approve_owner(
    owner_id: str,
    action: Literal["approve", "reject"] = Query(...),
    reason: Optional[str] = Query(None),

    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    owner = db.query(OwnerProfile).filter(
        OwnerProfile.user_id == owner_id
    ).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    # ❗ Reject must have reason
    if action == "reject" and not reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required"
        )

    # Optional safety
    if owner.verification_status == OwnerVerificationStatus.VERIFIED:
        raise HTTPException(400, "Owner already verified")

    if action == "approve":
        owner.verification_status = OwnerVerificationStatus.VERIFIED
        owner.rejection_reason = None

    else:
        owner.verification_status = OwnerVerificationStatus.REJECTED
        owner.rejection_reason = reason

    owner.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(owner)

    return {
        "message": f"Owner {action}d successfully",
        "owner_id": owner_id
    }