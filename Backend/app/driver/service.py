# app/driver/service.py

from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.db.schema import (
    User,
    UserRole,
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
    WalletTransaction,
    WalletTxnType,
    WalletTxnStatus,
    Payment,
    PaymentStatus,
    utcnow,
)
from app.driver.schemas import DriverProfileUpdate, BikeSearchQuery, CreateBookingRequest
from app.owner.service import save_uploaded_file
from app.notifications.service import create_notification



# ============================================================
# DRIVER PROFILE & KYC
# ============================================================

async def get_driver_kyc_service(db: Session, user: User) -> Dict[str, Any]:
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not prof:
        prof = DriverProfile(user_id=user.id, full_name=user.email.split("@")[0])
        db.add(prof)
        db.commit()
        db.refresh(prof)

    return {
        "user_id": user.id,
        "full_name": prof.full_name,
        "email": user.email,
        "phone": user.phone,
        "address": getattr(prof, "address", "") or "",
        "driving_license_number": prof.driving_license_number or "",
        "driving_license_file_path": prof.driving_license_file_path or "",
        "aadhaar_number": prof.aadhaar_number or "",
        "aadhaar_file_path": prof.aadhaar_file_path or "",
        "pan_number": getattr(prof, "pan_number", "") or "",
        "pan_file_path": getattr(prof, "pan_file_path", "") or "",
        "profile_picture_path": prof.profile_picture_path or "",
        "emergency_contact_name": prof.emergency_contact_name or "",
        "emergency_contact_phone": prof.emergency_contact_phone or "",
        "verification_status": prof.verification_status.value if hasattr(prof.verification_status, "value") else str(prof.verification_status),
        "rejection_reason": prof.rejection_reason or "",
        "verification_requested_at": prof.verification_requested_at.isoformat() if prof.verification_requested_at else None,
        "reviewed_at": prof.reviewed_at.isoformat() if prof.reviewed_at else None,
    }


async def submit_driver_kyc_service(
    db: Session,
    user: User,
    full_name: Optional[str] = None,
    driving_license_number: Optional[str] = None,
    aadhaar_number: Optional[str] = None,
    pan_number: Optional[str] = None,
    address: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    license_file: Optional[UploadFile] = None,
    aadhaar_file: Optional[UploadFile] = None,
    pan_file: Optional[UploadFile] = None,
    profile_picture: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if prof:
        # Prevent re-submission if KYC is currently under review or already verified
        if prof.verification_status == DriverVerificationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your KYC documents are currently under review by Admin. Submissions are locked until verification is complete.",
            )
        if prof.verification_status == DriverVerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your KYC documents have already been verified and approved. Re-submission is not allowed.",
            )
    else:
        prof = DriverProfile(user_id=user.id, full_name=full_name or user.email.split("@")[0])
        db.add(prof)

    if full_name and full_name.strip():
        prof.full_name = full_name.strip()
    if driving_license_number and driving_license_number.strip():
        prof.driving_license_number = driving_license_number.strip().upper()
    if aadhaar_number and aadhaar_number.strip():
        prof.aadhaar_number = aadhaar_number.strip().replace(" ", "")
    if pan_number and pan_number.strip():
        prof.pan_number = pan_number.strip().upper()
    if address and address.strip():
        prof.address = address.strip()
    if emergency_contact_name and emergency_contact_name.strip():
        prof.emergency_contact_name = emergency_contact_name.strip()
    if emergency_contact_phone and emergency_contact_phone.strip():
        prof.emergency_contact_phone = emergency_contact_phone.strip()

    # Save uploaded files to uploads/kyc
    if license_file and license_file.filename:
        prof.driving_license_file_path = save_uploaded_file(license_file, folder="uploads/kyc")
    if aadhaar_file and aadhaar_file.filename:
        prof.aadhaar_file_path = save_uploaded_file(aadhaar_file, folder="uploads/kyc")
    if pan_file and pan_file.filename:
        prof.pan_file_path = save_uploaded_file(pan_file, folder="uploads/kyc")
    if profile_picture and profile_picture.filename:
        prof.profile_picture_path = save_uploaded_file(profile_picture, folder="uploads/kyc")

    prof.verification_status = DriverVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()
    prof.rejection_reason = None

    db.commit()
    db.refresh(prof)

    create_notification(
        db,
        user.id,
        "KYC Submitted for Verification",
        "Your KYC documents (Driving License, Aadhaar, PAN & Photo) have been submitted to Admin for review.",
    )

    # Notify admins about pending KYC review
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    for adm in admins:
        create_notification(
            db,
            adm.id,
            "New Driver KYC Pending Review",
            f"Driver {prof.full_name} ({user.email}) has submitted KYC documents for verification.",
        )

    return {
        "message": "Driver KYC documents submitted successfully to Admin for verification.",
        "profile": await get_driver_kyc_service(db, user),
    }


async def update_driver_profile_service(
    db: Session, user: User, req: DriverProfileUpdate
) -> Dict[str, Any]:
    prof = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if prof:
        if prof.verification_status == DriverVerificationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your profile is currently under review by Admin. You cannot modify documents while status is pending.",
            )
        if prof.verification_status == DriverVerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your KYC profile is already verified. Re-submission is not allowed.",
            )
    else:
        prof = DriverProfile(user_id=user.id, full_name=user.email)
        db.add(prof)

    for field, val in req.dict(exclude_unset=True).items():
        setattr(prof, field, val)

    prof.verification_status = DriverVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()
    prof.rejection_reason = None

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

    if license_file and license_file.filename:
        prof.driving_license_file_path = save_uploaded_file(license_file, folder="uploads/kyc")
    if aadhaar_file and aadhaar_file.filename:
        prof.aadhaar_file_path = save_uploaded_file(aadhaar_file, folder="uploads/kyc")
    if profile_pic and profile_pic.filename:
        prof.profile_picture_path = save_uploaded_file(profile_pic, folder="uploads/kyc")

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
        tariffs_list = [
            {"id": t.id, "hours": t.hours, "price": float(t.price)}
            for t in b.tariffs
        ] if b.tariffs else []

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
            "hourly_rate": float(pricing.hourly_rate) if (pricing and pricing.hourly_rate) else 100.0,
            "security_deposit": float(pricing.security_deposit) if pricing else 0.0,
            "late_fee_per_day": float(pricing.late_fee_per_day) if pricing else 0.0,
            "late_fee_per_hour": float(pricing.late_fee_per_hour) if (pricing and pricing.late_fee_per_hour) else 50.0,
            "tariffs": tariffs_list,
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

    # 4. Calculate dynamic rent amount based on duration (hours) and tariffs
    pricing = bike.pricing
    daily_rent = pricing.daily_rent if pricing else Decimal("500.00")
    security_deposit = pricing.security_deposit if pricing else Decimal("1000.00")
    hourly_rate = pricing.hourly_rate if (pricing and pricing.hourly_rate) else Decimal("100.00")
    rental_hours = req.rental_hours if req.rental_hours and req.rental_hours > 0 else 24

    # Check for exact matching tariff
    matching_tariff = next((t for t in (bike.tariffs or []) if t.hours == rental_hours), None)
    if matching_tariff:
        rent_amount = matching_tariff.price
    elif rental_hours < 24:
        rent_amount = Decimal(rental_hours) * hourly_rate
    else:
        days = rental_hours // 24
        extra_h = rental_hours % 24
        rent_amount = (Decimal(days) * daily_rent) + (Decimal(extra_h) * hourly_rate)

    payment_method = (req.payment_method or "cod").lower()
    is_cod = payment_method == "cod"

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
        db.add(wallet)
        db.flush()

    total_required = Decimal("0.00")
    if not is_cod:
        # Online / UPI / Razorpay payment requires sufficient wallet balance or prepayment
        total_required = rent_amount + security_deposit
        if wallet.balance < total_required and not req.razorpay_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Booking failed due to insufficient wallet balance. Total required: INR {total_required} (Rent INR {rent_amount} + Security Deposit INR {security_deposit}). Available in wallet: INR {wallet.balance}. Please recharge minimum INR 500 or choose Cash on Delivery (COD).",
            )
        # Deduct held booking amount from wallet upfront
        wallet.balance -= total_required

    # 5. Create Booking Request
    booking = BikeBookingRequest(
        driver_user_id=user.id,
        bike_id=bike.id,
        rental_hours=rental_hours,
        total_amount=rent_amount,
        payment_method=payment_method,
        cash_received=not is_cod,
        cash_received_at=utcnow() if not is_cod else None,
        status=BookingRequestStatus.PENDING,
        message=req.message,
    )
    db.add(booking)
    db.flush()

    if not is_cod and total_required > Decimal("0.00"):
        txn = WalletTransaction(
            wallet_id=wallet.id,
            amount=total_required,
            txn_type=WalletTxnType.DEBIT,
            status=WalletTxnStatus.SUCCESS,
            reference_id=booking.id,
            description=f"Booking hold for {bike.bike_name} ({bike.registration_number}) - Rent ₹{rent_amount} + Deposit ₹{security_deposit}",
        )
        db.add(txn)

        payment = Payment(
            booking_request_id=booking.id,
            driver_user_id=user.id,
            amount=total_required,
            currency="INR",
            razorpay_order_id=req.razorpay_order_id or f"order_{booking.id[:8]}_{int(utcnow().timestamp())}",
            razorpay_payment_id=req.razorpay_payment_id or f"pay_wallet_{booking.id[:8]}",
            status=PaymentStatus.SUCCESS,
            paid_at=utcnow(),
        )
        db.add(payment)

    db.commit()
    db.refresh(booking)

    # 6. Notify owner
    notif_title = "New Booking Request" + (" (Cash on Delivery)" if is_cod else " (Online Payment)")
    notif_msg = f"A driver requested to rent {bike.bike_name} ({bike.registration_number}) for {rental_hours} hr(s) @ INR {rent_amount} via {payment_method.upper()}."
    create_notification(db, bike.owner_user_id, notif_title, notif_msg)
    try:
        from app.notifications.socket_manager import socket_manager
        socket_manager.notify_user_sync(
            bike.owner_user_id,
            {
                "booking_id": booking.id,
                "bike_name": bike.bike_name,
                "payment_method": payment_method,
                "rental_hours": rental_hours,
                "total_amount": float(rent_amount),
            },
            event_type="new_booking_request",
        )
    except Exception as e:
        print("[SOCKET WARNING] Could not send real-time notification:", e)

    return {
        "message": f"Booking request sent to bike owner ({'Cash on Delivery' if is_cod else 'Online Payment'}).",
        "booking_id": booking.id,
        "rental_hours": rental_hours,
        "payment_method": payment_method,
        "rent_amount": float(rent_amount),
        "security_deposit": float(security_deposit) if not is_cod else 0.0,
        "wallet_balance": float(wallet.balance),
    }


async def notify_cash_handed_service(db: Session, user: User, assignment_id: str) -> Dict[str, Any]:
    assignment = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.id == assignment_id,
        DriverBikeAssignment.driver_user_id == user.id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Active assignment not found")

    bike = assignment.bike
    reg = bike.registration_number if bike else ""
    amount = assignment.total_rent_amount or assignment.daily_rent_amount

    # Send notification to Owner
    create_notification(
        db,
        assignment.owner_user_id,
        "Driver Reports Cash Handed Over",
        f"Driver reports that cash payment of INR {amount} for {bike.bike_name if bike else 'Scooty'} ({reg}) was handed over. Please confirm receipt.",
    )
    from app.notifications.socket_manager import socket_manager
    socket_manager.notify_user_sync(
        assignment.owner_user_id,
        {"assignment_id": assignment.id, "amount": float(amount), "driver_user_id": user.id},
        event_type="cash_handed_by_driver",
    )

    return {"message": "Owner has been notified that you handed over the cash."}
