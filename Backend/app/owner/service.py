# app/owner/service.py

from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.db.schema import (
    User,
    OwnerProfile,
    OwnerVerificationStatus,
    Bike,
    BikeStatus,
    BikeVerificationStatus,
    BikePricing,
    BikeDocument,
    BikeImage,
    FuelType,
    BikeOwnershipType,
    BikeBookingRequest,
    BookingRequestStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    DriverSecurityDepositLedger,
    DepositTxnType,
    OwnerPayoutLedger,
    PayoutStatus,
    Wallet,
    WalletTransaction,
    WalletTxnType,
    WalletTxnStatus,
    utcnow,
)
from app.owner.schemas import (
    OwnerProfileUpdate,
    BikeCreateRequest,
    BookingDecisionRequest,
    ReturnBikeInspectionRequest,
)


# Helper for saving uploaded files
def save_uploaded_file(file: UploadFile, folder: str = "uploads") -> str:
    import os
    import uuid
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return filepath.replace("\\", "/")


# ============================================================
# PROFILE & KYC
# ============================================================

async def update_owner_profile_service(
    db: Session, user: User, req: OwnerProfileUpdate
) -> Dict[str, Any]:
    prof = db.query(OwnerProfile).filter(OwnerProfile.user_id == user.id).first()
    if not prof:
        prof = OwnerProfile(user_id=user.id, full_name=user.email, phone=user.phone)
        db.add(prof)

    for field, val in req.dict(exclude_unset=True).items():
        setattr(prof, field, val)

    prof.verification_status = OwnerVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()

    db.commit()
    db.refresh(prof)
    return {"message": "Owner profile updated and submitted for admin verification."}


async def upload_owner_documents_service(
    db: Session,
    user: User,
    aadhaar_file: Optional[UploadFile] = None,
    pan_file: Optional[UploadFile] = None,
    passbook_file: Optional[UploadFile] = None,
    profile_pic: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    prof = db.query(OwnerProfile).filter(OwnerProfile.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Owner profile not found")

    if aadhaar_file:
        prof.aadhaar_file_path = save_uploaded_file(aadhaar_file)
    if pan_file:
        prof.pan_file_path = save_uploaded_file(pan_file)
    if passbook_file:
        prof.passbook_file_path = save_uploaded_file(passbook_file)
    if profile_pic:
        prof.profile_picture_path = save_uploaded_file(profile_pic)

    prof.verification_status = OwnerVerificationStatus.PENDING
    prof.verification_requested_at = utcnow()

    db.commit()
    return {"message": "Owner KYC documents uploaded successfully."}


# ============================================================
# BIKE MANAGEMENT
# ============================================================

async def create_bike_listing_service(
    db: Session, user: User, req: BikeCreateRequest
) -> Dict[str, Any]:
    # Check registration number uniqueness
    if db.query(Bike).filter(Bike.registration_number == req.registration_number).first():
        raise HTTPException(status_code=400, detail="Bike with this registration number already exists.")

    fuel_enum = FuelType(req.fuel_type.lower())
    owner_enum = BikeOwnershipType(req.ownership_type.lower())

    bike = Bike(
        owner_user_id=user.id,
        bike_name=req.bike_name,
        brand=req.brand,
        model=req.model,
        registration_number=req.registration_number,
        color=req.color,
        fuel_type=fuel_enum,
        ownership_type=owner_enum,
        engine_number=req.engine_number,
        chassis_number=req.chassis_number,
        km_driven=req.km_driven,
        year_of_purchase=req.year_of_purchase,
        status=BikeStatus.INACTIVE,
        verification_status=BikeVerificationStatus.DRAFT,
        is_active=True,
    )
    db.add(bike)
    db.flush()

    pricing = BikePricing(
        bike_id=bike.id,
        daily_rent=req.daily_rent,
        weekly_rent=req.weekly_rent,
        monthly_rent=req.monthly_rent,
        security_deposit=req.security_deposit,
        late_fee_per_day=req.late_fee_per_day,
    )
    db.add(pricing)

    docs = BikeDocument(bike_id=bike.id)
    db.add(docs)

    db.commit()
    db.refresh(bike)

    return {
        "message": "Bike created in Draft mode. Upload documents and submit for verification.",
        "bike_id": bike.id,
    }


async def upload_bike_documents_service(
    db: Session,
    user: User,
    bike_id: str,
    rc_file: Optional[UploadFile] = None,
    insurance_file: Optional[UploadFile] = None,
    pollution_file: Optional[UploadFile] = None,
    permit_file: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    docs = db.query(BikeDocument).filter(BikeDocument.bike_id == bike.id).first()
    if not docs:
        docs = BikeDocument(bike_id=bike.id)
        db.add(docs)

    if rc_file:
        docs.rc_file_path = save_uploaded_file(rc_file)
    if insurance_file:
        docs.insurance_file_path = save_uploaded_file(insurance_file)
    if pollution_file:
        docs.pollution_file_path = save_uploaded_file(pollution_file)
    if permit_file:
        docs.permit_file_path = save_uploaded_file(permit_file)

    db.commit()
    return {"message": "Bike documents uploaded successfully."}


async def upload_bike_images_service(
    db: Session, user: User, bike_id: str, images: List[UploadFile]
) -> Dict[str, Any]:
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    saved_paths = []
    for idx, img in enumerate(images):
        filepath = save_uploaded_file(img)
        bike_img = BikeImage(bike_id=bike.id, image_path=filepath, sort_order=idx + 1)
        db.add(bike_img)
        saved_paths.append(filepath)

    db.commit()
    return {"message": f"{len(saved_paths)} bike images uploaded successfully.", "images": saved_paths}


async def submit_bike_for_verification(db: Session, user: User, bike_id: str) -> Dict[str, Any]:
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    bike.verification_status = BikeVerificationStatus.PENDING
    db.commit()
    return {"message": "Bike submitted to Admin for verification."}


# ============================================================
# BOOKING DECISIONS & RETURN INSPECTION
# ============================================================

async def handle_booking_request_service(
    db: Session, user: User, booking_id: str, req: BookingDecisionRequest
) -> Dict[str, Any]:
    booking = db.query(BikeBookingRequest).filter(BikeBookingRequest.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking request not found")

    bike = db.query(Bike).filter(Bike.id == booking.bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=403, detail="Not authorized to manage this booking")

    if booking.status != BookingRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Booking is already {booking.status.value}")

    if not req.accepted:
        booking.status = BookingRequestStatus.REJECTED
        booking.rejected_reason = req.rejection_reason or "Rejected by owner."
        db.commit()
        return {"message": "Booking request rejected."}

    # OWNER ACCEPTS BOOKING FLOW:
    # 1. Check driver active assignment
    active_assign = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.driver_user_id == booking.driver_user_id,
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
    ).first()
    if active_assign:
        booking.status = BookingRequestStatus.REJECTED
        booking.rejected_reason = "Driver already has an active bike assignment."
        db.commit()
        raise HTTPException(status_code=400, detail="Driver already has an active bike assignment.")

    # 2. Wallet balance check
    pricing = bike.pricing
    daily_rent = pricing.daily_rent if pricing else Decimal("500.00")
    security_deposit = pricing.security_deposit if pricing else Decimal("1000.00")
    total_required = daily_rent + security_deposit

    driver_wallet = db.query(Wallet).filter(Wallet.user_id == booking.driver_user_id).first()
    if not driver_wallet or driver_wallet.balance < total_required:
        booking.status = BookingRequestStatus.REJECTED
        booking.rejected_reason = f"Insufficient wallet balance. Required ₹{total_required}, available ₹{driver_wallet.balance if driver_wallet else 0}"
        db.commit()
        raise HTTPException(status_code=400, detail=f"Driver wallet balance (₹{driver_wallet.balance if driver_wallet else 0}) is less than required booking amount (₹{total_required}).")

    # 3. Deduct wallet & create transaction ledger
    driver_wallet.balance -= total_required
    txn = WalletTransaction(
        wallet_id=driver_wallet.id,
        amount=total_required,
        txn_type=WalletTxnType.DEBIT,
        status=WalletTxnStatus.SUCCESS,
        reference_id=booking.id,
        description=f"Rent & Security deposit deduction for bike {bike.bike_name} ({bike.registration_number})",
    )
    db.add(txn)

    # 4. Approve booking & create DriverBikeAssignment
    booking.status = BookingRequestStatus.APPROVED
    booking.approved_at = utcnow()

    assignment = DriverBikeAssignment(
        driver_user_id=booking.driver_user_id,
        owner_user_id=user.id,
        bike_id=bike.id,
        daily_rent_amount=daily_rent,
        security_deposit_amount=security_deposit,
        status=AssignmentStatus.ACTIVE,
    )
    db.add(assignment)
    db.flush()

    # 5. Lock bike status
    bike.status = BikeStatus.ASSIGNED

    # 6. Record security deposit ledger
    dep_ledger = DriverSecurityDepositLedger(
        assignment_id=assignment.id,
        txn_type=DepositTxnType.CREDIT,
        amount=security_deposit,
        note="Initial deposit collected",
    )
    db.add(dep_ledger)


    db.commit()
    return {
        "message": "Booking accepted and bike assigned to driver.",
        "assignment_id": assignment.id,
        "amount_deducted": float(total_required),
    }


async def inspect_and_complete_return_service(
    db: Session, user: User, req: ReturnBikeInspectionRequest
) -> Dict[str, Any]:
    assignment = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.id == req.assignment_id,
        DriverBikeAssignment.owner_user_id == user.id,
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Active assignment not found")

    deposit = assignment.security_deposit_amount
    damage = req.damage_charge if req.is_damaged else Decimal("0.00")
    refund_amount = deposit - damage
    if refund_amount < Decimal("0.00"):
        refund_amount = Decimal("0.00")

    # Driver wallet refund
    driver_wallet = db.query(Wallet).filter(Wallet.user_id == assignment.driver_user_id).first()
    if driver_wallet and refund_amount > Decimal("0.00"):
        driver_wallet.balance += refund_amount
        txn = WalletTransaction(
            wallet_id=driver_wallet.id,
            amount=refund_amount,
            txn_type=WalletTxnType.REFUND,
            status=WalletTxnStatus.SUCCESS,
            reference_id=assignment.id,
            description=f"Security deposit refund after bike return (Damage charge: INR {damage})",
        )
        db.add(txn)

    # End assignment & release bike
    assignment.status = AssignmentStatus.ENDED
    assignment.ended_at = utcnow()
    assignment.ended_reason = f"Returned by driver. Damaged: {req.is_damaged}. Notes: {req.notes or 'N/A'}"

    bike = db.query(Bike).filter(Bike.id == assignment.bike_id).first()
    if bike:
        bike.status = BikeStatus.AVAILABLE

    db.commit()
    return {
        "message": "Bike return processed successfully.",
        "damage_charged": float(damage),
        "deposit_refunded": float(refund_amount),
    }
