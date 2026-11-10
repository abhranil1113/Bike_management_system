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
    BikeTariff,
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
    Payment,
    PaymentStatus,
    utcnow,
)
from app.owner.schemas import (
    OwnerProfileUpdate,
    BikeCreateRequest,
    BookingDecisionRequest,
    ReturnBikeInspectionRequest,
    TariffTier,
    TariffsUpdateRequest,
    CashStatusUpdateRequest,
)
from app.notifications.service import create_notification
from app.notifications.socket_manager import socket_manager



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
    create_notification(
        db,
        user.id,
        "Verification Submitted",
        "Your verification documents have been submitted successfully and are waiting for admin review.",
    )
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
    create_notification(
        db,
        user.id,
        "Verification Submitted",
        "Your verification documents have been submitted successfully and are waiting for admin review.",
    )
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
        hourly_rate=req.hourly_rate if req.hourly_rate is not None else Decimal("100.00"),
        weekly_rent=req.weekly_rent,
        monthly_rent=req.monthly_rent,
        security_deposit=req.security_deposit,
        late_fee_per_day=req.late_fee_per_day,
        late_fee_per_hour=req.late_fee_per_hour if req.late_fee_per_hour is not None else Decimal("50.00"),
    )
    db.add(pricing)

    # Add custom time-based tariffs if supplied
    if req.tariffs:
        for t in req.tariffs:
            tariff_entry = BikeTariff(
                bike_id=bike.id,
                hours=t.hours,
                price=t.price,
            )
            db.add(tariff_entry)
    else:
        # Default starter tariffs if none provided
        default_tiers = [
            (1, req.hourly_rate or Decimal("100.00")),
            (2, (req.hourly_rate or Decimal("100.00")) * 2),
            (4, (req.hourly_rate or Decimal("100.00")) * Decimal("3.8")),
            (8, (req.hourly_rate or Decimal("100.00")) * Decimal("7.0")),
            (12, (req.hourly_rate or Decimal("100.00")) * Decimal("10.0")),
            (24, req.daily_rent),
        ]
        for h, p in default_tiers:
            db.add(BikeTariff(bike_id=bike.id, hours=h, price=Decimal(str(round(float(p), 2)))))

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
    create_notification(
        db,
        user.id,
        "Bike Submitted",
        "Your bike has been submitted for verification.",
    )
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

    is_accepted = req.accepted if req.accepted is not None else (
        req.decision.strip().lower() in ("accept", "approved", "approve", "true", "1")
        if req.decision else False
    )

    if not is_accepted:
        rej_reason = req.rejection_reason or "Rejected by bike owner."
        is_cod = (getattr(booking, "payment_method", "cod") or "cod").lower() == "cod"
        refund_amount = Decimal("0.00")

        if not is_cod:
            # Check debit txn or payment for this booking to calculate exact refund amount
            debit_txn = db.query(WalletTransaction).filter(
                WalletTransaction.reference_id == booking.id,
                WalletTransaction.txn_type == WalletTxnType.DEBIT,
                WalletTransaction.status == WalletTxnStatus.SUCCESS,
            ).first()
            if debit_txn:
                refund_amount = debit_txn.amount
            else:
                payment = db.query(Payment).filter(Payment.booking_request_id == booking.id).first()
                if payment:
                    refund_amount = payment.amount
                elif booking.total_amount:
                    pricing = bike.pricing
                    sec_dep = pricing.security_deposit if pricing else Decimal("1000.00")
                    refund_amount = booking.total_amount + sec_dep

            if refund_amount > Decimal("0.00"):
                driver_wallet = db.query(Wallet).filter(Wallet.user_id == booking.driver_user_id).first()
                if not driver_wallet:
                    driver_wallet = Wallet(user_id=booking.driver_user_id, balance=Decimal("0.00"))
                    db.add(driver_wallet)
                    db.flush()
                driver_wallet.balance += refund_amount
                refund_txn = WalletTransaction(
                    wallet_id=driver_wallet.id,
                    amount=refund_amount,
                    txn_type=WalletTxnType.REFUND,
                    status=WalletTxnStatus.SUCCESS,
                    reference_id=booking.id,
                    description=f"Refund for rejected booking #{booking.id[:8]} - {bike.bike_name} ({bike.registration_number})",
                )
                db.add(refund_txn)

            # Update Payment status to REFUNDED
            payments = db.query(Payment).filter(Payment.booking_request_id == booking.id).all()
            for p in payments:
                p.status = PaymentStatus.REFUNDED

        booking.status = BookingRequestStatus.REJECTED
        booking.rejected_reason = rej_reason
        bike.status = BikeStatus.AVAILABLE
        db.commit()

        rej_msg = (
            f"Your booking request for {bike.bike_name} ({bike.registration_number}) was rejected by the owner. Reason: {rej_reason}."
            + (f" ₹{refund_amount} has been refunded back to your wallet." if refund_amount > Decimal("0.00") else "")
        )
        create_notification(db, booking.driver_user_id, "Booking Rejected", rej_msg)
        socket_manager.notify_user_sync(
            booking.driver_user_id,
            {
                "booking_id": booking.id,
                "status": "rejected",
                "refund_amount": float(refund_amount),
                "reason": rej_reason,
            },
            event_type="booking_rejected",
        )
        return {
            "message": f"Booking request rejected.{f' ₹{refund_amount} refunded to driver wallet.' if refund_amount > Decimal('0.00') else ''}",
            "refund_amount": float(refund_amount),
        }

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

    pricing = bike.pricing
    daily_rent = pricing.daily_rent if pricing else Decimal("500.00")
    security_deposit = pricing.security_deposit if pricing else Decimal("1000.00")
    rent_to_charge = booking.total_amount if (booking.total_amount and booking.total_amount > Decimal("0.00")) else daily_rent
    rental_hours = booking.rental_hours or 24
    is_cod = (getattr(booking, "payment_method", "cod") or "cod").lower() == "cod"

    if is_cod:
        # Cash on Delivery: Hand-to-hand cash given directly to owner on pickup/delivery
        # No driver wallet deduction required upfront
        booking.status = BookingRequestStatus.APPROVED
        booking.approved_at = utcnow()
        booking.cash_received = False

        assignment = DriverBikeAssignment(
            driver_user_id=booking.driver_user_id,
            owner_user_id=user.id,
            bike_id=bike.id,
            rental_hours=rental_hours,
            daily_rent_amount=rent_to_charge,
            total_rent_amount=rent_to_charge,
            security_deposit_amount=Decimal("0.00"),
            payment_method="cod",
            cash_received=False,
            cash_received_at=None,
            cod_admin_escalated=False,
            status=AssignmentStatus.ACTIVE,
        )
        db.add(assignment)
        db.flush()

        bike.status = BikeStatus.ASSIGNED
        db.commit()

        create_notification(
            db,
            booking.driver_user_id,
            "Booking Approved (Cash on Delivery)",
            f"Your booking for {bike.bike_name} ({bike.registration_number}) is approved! Please hand over ₹{rent_to_charge} in cash to the owner upon vehicle pickup.",
        )
        socket_manager.notify_user_sync(
            booking.driver_user_id,
            {
                "booking_id": booking.id,
                "assignment_id": assignment.id,
                "payment_method": "cod",
                "cash_received": False,
                "amount": float(rent_to_charge),
            },
            event_type="booking_accepted",
        )

        return {
            "message": "Booking accepted (Cash on Delivery). Vehicle dispatched to driver.",
            "assignment_id": assignment.id,
            "payment_method": "cod",
            "cash_received": False,
            "amount_due": float(rent_to_charge),
        }

    # ONLINE / RAZORPAY / WALLET FLOW
    total_required = rent_to_charge + security_deposit
    driver_wallet = db.query(Wallet).filter(Wallet.user_id == booking.driver_user_id).first()

    # Check if booking amount was already held during booking creation
    debit_txn = db.query(WalletTransaction).filter(
        WalletTransaction.reference_id == booking.id,
        WalletTransaction.txn_type == WalletTxnType.DEBIT,
        WalletTransaction.status == WalletTxnStatus.SUCCESS,
    ).first()

    if not debit_txn:
        # If not already debited upfront (e.g. legacy booking request), deduct now
        if not driver_wallet or driver_wallet.balance < total_required:
            booking.status = BookingRequestStatus.REJECTED
            booking.rejected_reason = f"Insufficient wallet balance. Required ₹{total_required}, available ₹{driver_wallet.balance if driver_wallet else 0}"
            db.commit()
            raise HTTPException(status_code=400, detail=f"Driver wallet balance (₹{driver_wallet.balance if driver_wallet else 0}) is less than required booking amount (₹{total_required}).")

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

    booking.status = BookingRequestStatus.APPROVED
    booking.approved_at = utcnow()
    booking.cash_received = True
    booking.cash_received_at = utcnow()

    assignment = DriverBikeAssignment(
        driver_user_id=booking.driver_user_id,
        owner_user_id=user.id,
        bike_id=bike.id,
        rental_hours=rental_hours,
        daily_rent_amount=rent_to_charge,
        total_rent_amount=rent_to_charge,
        security_deposit_amount=security_deposit,
        payment_method="razorpay",
        cash_received=True,
        cash_received_at=utcnow(),
        cod_admin_escalated=False,
        status=AssignmentStatus.ACTIVE,
    )
    db.add(assignment)
    db.flush()

    bike.status = BikeStatus.ASSIGNED

    dep_ledger = DriverSecurityDepositLedger(
        assignment_id=assignment.id,
        txn_type=DepositTxnType.CREDIT,
        amount=security_deposit,
        note="Initial deposit collected",
    )
    db.add(dep_ledger)
    db.commit()

    create_notification(
        db,
        booking.driver_user_id,
        "Booking Approved (Online Payment)",
        f"Your booking for {bike.bike_name} ({bike.registration_number}) has been approved and prepaid online.",
    )
    socket_manager.notify_user_sync(
        booking.driver_user_id,
        {
            "booking_id": booking.id,
            "assignment_id": assignment.id,
            "payment_method": "razorpay",
            "cash_received": True,
            "amount": float(rent_to_charge),
        },
        event_type="booking_accepted",
    )

    return {
        "message": "Booking accepted and bike assigned to driver.",
        "assignment_id": assignment.id,
        "payment_method": "razorpay",
        "cash_received": True,
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
    create_notification(
        db,
        assignment.driver_user_id,
        "Assignment Ended",
        "Your current bike assignment has ended.",
    )
    return {
        "message": "Bike return processed successfully.",
        "damage_charged": float(damage),
        "deposit_refunded": float(refund_amount),
    }


async def update_assignment_cash_status_service(
    db: Session, user: User, assignment_id: str, req: CashStatusUpdateRequest
) -> Dict[str, Any]:
    assignment = (
        db.query(DriverBikeAssignment)
        .filter(
            DriverBikeAssignment.id == assignment_id,
            DriverBikeAssignment.owner_user_id == user.id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Bike rental assignment not found.")

    bike = assignment.bike
    bike_label = f"{bike.bike_name} ({bike.registration_number})" if bike else "Scooty"
    amount = assignment.total_rent_amount or assignment.daily_rent_amount

    assignment.cash_received = req.cash_received
    if req.cash_received:
        assignment.cash_received_at = utcnow()
        # Update matching booking request
        booking = (
            db.query(BikeBookingRequest)
            .filter(
                BikeBookingRequest.bike_id == assignment.bike_id,
                BikeBookingRequest.driver_user_id == assignment.driver_user_id,
            )
            .order_by(BikeBookingRequest.created_at.desc())
            .first()
        )
        if booking:
            booking.cash_received = True
            booking.cash_received_at = assignment.cash_received_at

        create_notification(
            db,
            assignment.driver_user_id,
            "Cash Payment Received",
            f"Owner has confirmed receipt of cash payment ₹{amount} for {bike_label}. Thank you!",
        )
        socket_manager.notify_user_sync(
            assignment.driver_user_id,
            {
                "assignment_id": assignment.id,
                "cash_received": True,
                "amount": float(amount),
                "message": f"Owner confirmed cash payment of ₹{amount}.",
            },
            event_type="cash_status_updated",
        )
    else:
        assignment.cash_received_at = None
        create_notification(
            db,
            assignment.driver_user_id,
            "Cash Payment Marked Not Received",
            f"Owner has marked cash payment of ₹{amount} for {bike_label} as NOT RECEIVED. Please hand over cash to the owner immediately.",
        )
        socket_manager.notify_user_sync(
            assignment.driver_user_id,
            {
                "assignment_id": assignment.id,
                "cash_received": False,
                "amount": float(amount),
                "message": f"Owner marked cash payment as not received.",
            },
            event_type="cash_status_updated",
        )

    db.commit()
    db.refresh(assignment)

    return {
        "message": f"Cash receipt status updated to {'RECEIVED' if req.cash_received else 'NOT RECEIVED'}.",
        "assignment_id": assignment.id,
        "cash_received": assignment.cash_received,
        "cash_received_at": assignment.cash_received_at.isoformat() if assignment.cash_received_at else None,
    }


async def get_bike_tariffs_service(db: Session, user: User, bike_id: str) -> List[Dict[str, Any]]:
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    tariffs = db.query(BikeTariff).filter(BikeTariff.bike_id == bike.id).order_by(BikeTariff.hours.asc()).all()
    return [
        {
            "id": t.id,
            "bike_id": t.bike_id,
            "hours": t.hours,
            "price": float(t.price),
        }
        for t in tariffs
    ]


async def update_bike_tariffs_service(
    db: Session, user: User, bike_id: str, req: TariffsUpdateRequest
) -> Dict[str, Any]:
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.owner_user_id == user.id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    db.query(BikeTariff).filter(BikeTariff.bike_id == bike.id).delete()
    for t in req.tariffs:
        db.add(BikeTariff(bike_id=bike.id, hours=t.hours, price=t.price))

    db.commit()
    return {"message": f"Successfully updated {len(req.tariffs)} time-based tariffs."}
