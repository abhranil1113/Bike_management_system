from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.db.schema import (
    Bike,
    BikeBookingRequest,
    BikeStatus,
    UserRole,
    DriverBikeAssignment,
    BookingRequestStatus,
    BikeVerificationStatus,
    DriverVerificationStatus,
    OwnerVerificationStatus,
    DriverProfile,
    OwnerProfile,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/booking", tags=["Booking"])


# =========================================================
# CREATE BOOKING REQUEST (DRIVER)
# =========================================================

@router.post("/request")
def create_booking_request(
    bike_id: str,
    message: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # Only driver allowed
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(403, "Only drivers can book bikes")

    # Driver verification check
    driver_profile = db.query(DriverProfile).filter(
        DriverProfile.user_id == current_user.id
    ).first()

    if not driver_profile or driver_profile.verification_status != DriverVerificationStatus.VERIFIED:
        raise HTTPException(400, "Driver not verified")

    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    # Bike verification check
    if bike.verification_status != BikeVerificationStatus.VERIFIED:
        raise HTTPException(400, "Bike not verified")

    if bike.status != BikeStatus.AVAILABLE:
        raise HTTPException(400, "Bike not available")

    # Owner verification check
    owner_profile = db.query(OwnerProfile).filter(
        OwnerProfile.user_id == bike.owner_user_id
    ).first()

    if not owner_profile or owner_profile.verification_status != OwnerVerificationStatus.VERIFIED:
        raise HTTPException(400, "Owner not verified")

    # Prevent duplicate request
    existing = db.query(BikeBookingRequest).filter(
        BikeBookingRequest.driver_user_id == current_user.id,
        BikeBookingRequest.bike_id == bike_id,
        BikeBookingRequest.status == BookingRequestStatus.PENDING,
    ).first()

    if existing:
        raise HTTPException(400, "Already requested")

    booking = BikeBookingRequest(
        driver_user_id=current_user.id,
        bike_id=bike_id,
        message=message,
        status=BookingRequestStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking request created",
        "booking_id": booking.id,
        "status": booking.status,
    }


# =========================================================
# OWNER: VIEW REQUESTS
# =========================================================

@router.get("/owner/requests")
def get_owner_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if current_user.role != UserRole.OWNER:
        raise HTTPException(403, "Only owners allowed")

    requests = db.query(BikeBookingRequest).join(Bike).filter(
        Bike.owner_user_id == current_user.id
    ).all()

    result = []

    for req in requests:
        result.append({
            "request_id": req.id,
            "bike_id": req.bike_id,
            "driver_id": req.driver_user_id,
            "status": req.status,
            "message": req.message,
            "approved_at": req.approved_at,
            "rejected_reason": req.rejected_reason,
        })

    return {
        "count": len(result),
        "data": result
    }


# =========================================================
# APPROVE REQUEST (OWNER)
# =========================================================

@router.patch("/{request_id}/approve")
def approve_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if current_user.role != UserRole.OWNER:
        raise HTTPException(403, "Only owners allowed")

    booking = db.query(BikeBookingRequest).filter_by(id=request_id).first()

    if not booking:
        raise HTTPException(404, "Request not found")

    if booking.status != BookingRequestStatus.PENDING:
        raise HTTPException(400, "Already processed")

    bike = db.query(Bike).filter(Bike.id == booking.bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    if bike.status != BikeStatus.AVAILABLE:
        raise HTTPException(400, "Bike already assigned")

    # Pricing safety
    if not bike.pricing:
        raise HTTPException(400, "Bike pricing not set")

    assignment = DriverBikeAssignment(
        driver_user_id=booking.driver_user_id,
        owner_user_id=bike.owner_user_id,
        bike_id=bike.id,
        daily_rent_amount=bike.pricing.daily_rent,
        security_deposit_amount=bike.pricing.security_deposit,
    )

    booking.status = BookingRequestStatus.APPROVED
    booking.approved_at = datetime.utcnow()

    bike.status = BikeStatus.ASSIGNED

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
    except Exception:
        db.rollback()
        raise HTTPException(500, "Approval failed")

    return {
        "message": "Approved and assigned",
        "assignment_id": assignment.id
    }


# =========================================================
# REJECT REQUEST (OWNER)
# =========================================================

@router.patch("/{request_id}/reject")
def reject_request(
    request_id: str,
    reason: str = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if current_user.role != UserRole.OWNER:
        raise HTTPException(403, "Only owners allowed")

    booking = db.query(BikeBookingRequest).filter_by(id=request_id).first()

    if not booking:
        raise HTTPException(404, "Request not found")

    if booking.status != BookingRequestStatus.PENDING:
        raise HTTPException(400, "Already processed")

    bike = db.query(Bike).filter(Bike.id == booking.bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    booking.status = BookingRequestStatus.REJECTED
    booking.rejected_reason = reason

    db.commit()

    return {
        "message": "Rejected",
        "request_id": request_id
    }