# app/driver/service.py

from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.db.schema import (
    User,
    DriverProfile,
    DriverVerificationStatus,
    Bike,
    BikeStatus,
    BikeVerificationStatus,
    BikePricing,
    BikeBookingRequest,
    BookingRequestStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    Wallet,
    utcnow,
)
from app.driver.schemas import DriverProfileUpdate, BikeSearchQuery, CreateBookingRequest
from app.owner.service import save_uploaded_file
from app.notifications.service import create_notification



# ============================================================
# DRIVER PROFILE & KYC
# ============================================================

async def update_driver_profile_service(
    db: Session, user: User, req: DriverProfileUpdate
) -> Dict[str, Any]:
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not prof:
        prof = DriverProfile(user_id=user.id, full_name=user.email)
        db.add(prof)

    for field, val in req.dict(exclude_unset=True).items():
        setattr(prof, field, val)

    prof.verification_status = DriverVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()

    db.commit()
    db.refresh(prof)
    create_notification(
        db,
        user.id,
        "Verification Submitted",
        "Your verification documents have been submitted successfully and are under review.",
    )
    return {"message": "Driver profile updated and submitted for admin verification."}


async def upload_driver_documents_service(
    db: Session,
    user: User,
    license_file: Optional[UploadFile] = None,
    aadhaar_file: Optional[UploadFile] = None,
    profile_pic: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    if license_file:
        prof.driving_license_file_path = save_uploaded_file(license_file)
    if aadhaar_file:
        prof.aadhaar_file_path = save_uploaded_file(aadhaar_file)
    if profile_pic:
        prof.profile_picture_path = save_uploaded_file(profile_pic)

    prof.verification_status = DriverVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()

    db.commit()
    create_notification(
        db,
        user.id,
        "Verification Submitted",
        "Your verification documents have been submitted successfully and are under review.",
    )
    return {"message": "Driver KYC documents uploaded successfully."}


# ============================================================
# SEARCH & BOOKING
# ============================================================

async def search_available_bikes_service(
    db: Session, query: BikeSearchQuery
) -> List[Dict[str, Any]]:
    q = db.query(Bike).join(BikePricing).filter(
        Bike.status == BikeStatus.AVAILABLE,
        Bike.verification_status == BikeVerificationStatus.VERIFIED,
        Bike.is_active == True,
    )

    if query.brand:
        q = q.filter(Bike.brand.ilike(f"%{query.brand}%"))
    if query.fuel_type:
        q = q.filter(Bike.fuel_type == query.fuel_type.lower())
    if query.max_daily_rent:
        q = q.filter(BikePricing.daily_rent <= query.max_daily_rent)

    bikes = q.all()
    results = []
    for b in bikes:
        pricing = b.pricing
        img_urls = [img.image_path for img in b.images]
        results.append({
            "id": b.id,
            "bike_name": b.bike_name,
            "brand": b.brand,
            "model": b.model,
            "registration_number": b.registration_number,
            "fuel_type": b.fuel_type.value,
            "ownership_type": b.ownership_type.value,
            "km_driven": b.km_driven,
            "daily_rent": float(pricing.daily_rent) if pricing else 0.0,
            "security_deposit": float(pricing.security_deposit) if pricing else 0.0,
            "late_fee_per_day": float(pricing.late_fee_per_day) if pricing else 0.0,
            "images": img_urls,
        })
    return results


async def request_bike_booking_service(
    db: Session, user: User, req: CreateBookingRequest
) -> Dict[str, Any]:
    # Driver KYC check
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not prof or prof.verification_status != DriverVerificationStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver account must be verified by Admin before booking a bike.",
        )

    # 1. Rule: Driver can only rent ONE bike at a time (Check active assignment)
    active_assignment = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.driver_user_id == user.id,
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
    ).first()
    if active_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver already has an active bike rental assignment. You can only rent one bike at a time.",
        )

    # 2. Check pending booking requests for driver
    pending_req = db.query(BikeBookingRequest).filter(
        BikeBookingRequest.driver_user_id == user.id,
        BikeBookingRequest.status == BookingRequestStatus.PENDING,
    ).first()
    if pending_req:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending booking request. Please wait for owner response.",
        )

    # 3. Check bike availability
    bike = db.query(Bike).filter(
        Bike.id == req.bike_id,
        Bike.status == BikeStatus.AVAILABLE,
        Bike.verification_status == BikeVerificationStatus.VERIFIED,
    ).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike is not available for booking.")

    # 4. Check wallet balance vs booking amount
    pricing = bike.pricing
    daily_rent = pricing.daily_rent if pricing else Decimal("500.00")
    security_deposit = pricing.security_deposit if pricing else Decimal("1000.00")
    total_required = daily_rent + security_deposit

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet or wallet.balance < total_required:
        available_bal = wallet.balance if wallet else Decimal("0.00")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking failed due to insufficient wallet balance. Total required: INR {total_required} (Daily Rent INR {daily_rent} + Security Deposit INR {security_deposit}). Available in wallet: INR {available_bal}. Minimum wallet recharge is INR 500.",
        )

    # Create Booking Request
    booking = BikeBookingRequest(
        driver_user_id=user.id,
        bike_id=bike.id,
        status=BookingRequestStatus.PENDING,
        message=req.message,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    create_notification(
        db,
        bike.owner_user_id,
        "New Booking Request",
        "A driver has requested to book your bike.",
    )

    return {
        "message": "Booking request sent to bike owner.",
        "booking_id": booking.id,
        "required_amount": float(total_required),
        "wallet_balance": float(wallet.balance),
    }
