# app/driver/router.py

from typing import Optional, List
from decimal import Decimal
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import (
    User,
    DriverBikeAssignment,
    BikeBookingRequest,
    BookingRequestStatus,
    AssignmentStatus,
    Wallet,
    WalletTransaction,
    WalletTxnType,
    WalletTxnStatus,
    Payment,
    PaymentStatus,
    Bike,
)
from app.api.deps import get_current_driver
from app.schemas.auth_schema import StandardResponse
from app.driver.schemas import DriverProfileUpdate, BikeSearchQuery, CreateBookingRequest
from app.driver.service import (
    get_driver_kyc_service,
    submit_driver_kyc_service,
    update_driver_profile_service,
    upload_driver_documents_service,
    search_available_bikes_service,
    request_bike_booking_service,
    notify_cash_handed_service,
)

router = APIRouter(prefix="/driver", tags=["Driver Operations"])


@router.get("/kyc", response_model=StandardResponse, summary="Get Driver KYC Dossier & Status")
@router.get("/profile", response_model=StandardResponse, summary="Get Driver Profile & KYC Dossier")
async def get_driver_kyc_api(
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    data = await get_driver_kyc_service(db, driver)
    return StandardResponse(success=True, message="Driver KYC fetched successfully.", data=data)


@router.post("/kyc", response_model=StandardResponse, summary="Submit Driver KYC Documents & Details (Multipart)")
@router.post("/kyc-documents", response_model=StandardResponse, summary="Submit Driver KYC Documents & Details (Multipart)")
async def submit_driver_kyc_api(
    full_name: Optional[str] = Form(None),
    driving_license_number: Optional[str] = Form(None),
    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    emergency_contact_name: Optional[str] = Form(None),
    emergency_contact_phone: Optional[str] = Form(None),
    license_file: Optional[UploadFile] = File(None),
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    profile_picture: Optional[UploadFile] = File(None),
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    res = await submit_driver_kyc_service(
        db,
        driver,
        full_name=full_name,
        driving_license_number=driving_license_number,
        aadhaar_number=aadhaar_number,
        pan_number=pan_number,
        address=address,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
        license_file=license_file,
        aadhaar_file=aadhaar_file,
        pan_file=pan_file,
        profile_picture=profile_picture,
    )
    return StandardResponse(success=True, message=res["message"], data=res.get("profile"))


@router.put("/profile", response_model=StandardResponse, summary="Update Driver Profile Details")
async def update_profile_api(
    req: DriverProfileUpdate,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    res = await update_driver_profile_service(db, driver, req)
    return StandardResponse(success=True, message=res["message"])


@router.get("/bikes", response_model=StandardResponse, summary="List All Available Verified Scooties")
async def list_available_bikes_api(
    brand: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    max_daily_rent: Optional[Decimal] = Query(None),
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    query = BikeSearchQuery(brand=brand, fuel_type=fuel_type, max_daily_rent=max_daily_rent)
    bikes = await search_available_bikes_service(db, query)
    return StandardResponse(success=True, message=f"Found {len(bikes)} available scooties.", data=bikes)


@router.post("/bikes/search", response_model=StandardResponse, summary="Search Available Verified Bikes")
async def search_bikes_api(
    query: BikeSearchQuery,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    bikes = await search_available_bikes_service(db, query)
    return StandardResponse(success=True, message=f"Found {len(bikes)} available bikes.", data=bikes)


@router.post("/bikes/book", response_model=StandardResponse, summary="Request Bike Rental Booking")
@router.post("/bookings", response_model=StandardResponse, summary="Request Bike Rental Booking")
async def request_booking_api(
    req: CreateBookingRequest,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    res = await request_bike_booking_service(db, driver, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/bookings/{booking_id}/cancel", response_model=StandardResponse, summary="Cancel Pending Booking Request")
async def cancel_booking_api(
    booking_id: str,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    booking = db.query(BikeBookingRequest).filter(
        BikeBookingRequest.id == booking_id,
        BikeBookingRequest.driver_user_id == driver.id,
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking request not found")

    if booking.status != BookingRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot cancel booking with status {booking.status.value}")

    is_cod = (getattr(booking, "payment_method", "cod") or "cod").lower() == "cod"
    refund_amount = Decimal("0.00")

    if not is_cod:
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
                bike = db.query(Bike).filter(Bike.id == booking.bike_id).first()
                sec_dep = bike.pricing.security_deposit if bike and bike.pricing else Decimal("1000.00")
                refund_amount = booking.total_amount + sec_dep

        if refund_amount > Decimal("0.00"):
            wallet = db.query(Wallet).filter(Wallet.user_id == driver.id).first()
            if not wallet:
                wallet = Wallet(user_id=driver.id, balance=Decimal("0.00"))
                db.add(wallet)
                db.flush()
            wallet.balance += refund_amount
            refund_txn = WalletTransaction(
                wallet_id=wallet.id,
                amount=refund_amount,
                txn_type=WalletTxnType.REFUND,
                status=WalletTxnStatus.SUCCESS,
                reference_id=booking.id,
                description=f"Refund for cancelled booking #{booking.id[:8]} - {booking.bike.bike_name if booking.bike else 'Scooty'}",
            )
            db.add(refund_txn)

        payments = db.query(Payment).filter(Payment.booking_request_id == booking.id).all()
        for p in payments:
            p.status = PaymentStatus.REFUNDED

    booking.status = BookingRequestStatus.CANCELLED
    booking.rejected_reason = "Cancelled by driver."

    from app.notifications.service import create_notification
    if booking.bike:
        create_notification(
            db,
            booking.bike.owner_user_id,
            "Booking Request Cancelled",
            f"The driver cancelled their pending booking request for {booking.bike.bike_name} ({booking.bike.registration_number}).",
        )

    db.commit()

    return StandardResponse(
        success=True,
        message=f"Booking request cancelled successfully.{f' ₹{refund_amount} has been refunded to your wallet.' if refund_amount > Decimal('0.00') else ''}",
        data={"booking_id": booking.id, "refund_amount": float(refund_amount)},
    )


@router.get("/assignment/active", response_model=StandardResponse, summary="Get Driver's Current Active Bike Assignment")
@router.get("/active-assignment", response_model=StandardResponse, summary="Get Driver's Current Active Bike Assignment")
async def get_active_assignment_api(
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    assignment = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.driver_user_id == driver.id,
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
    ).first()

    if not assignment:
        return StandardResponse(success=True, message="No active assignment.", data=None)

    data = {
        "id": assignment.id,
        "bike_id": assignment.bike_id,
        "bike_name": assignment.bike.bike_name,
        "registration_number": assignment.bike.registration_number,
        "assigned_at": assignment.assigned_at.isoformat(),
        "daily_rent": float(assignment.daily_rent_amount),
        "total_rent_amount": float(getattr(assignment, "total_rent_amount", assignment.daily_rent_amount) or assignment.daily_rent_amount),
        "rental_hours": getattr(assignment, "rental_hours", 24) or 24,
        "payment_method": getattr(assignment, "payment_method", "cod") or "cod",
        "cash_received": getattr(assignment, "cash_received", False) or False,
        "cash_received_at": assignment.cash_received_at.isoformat() if getattr(assignment, "cash_received_at", None) else None,
        "cod_admin_escalated": getattr(assignment, "cod_admin_escalated", False) or False,
        "security_deposit": float(assignment.security_deposit_amount),
        "status": assignment.status.value,
    }
    return StandardResponse(success=True, message="Active assignment retrieved.", data=data)


@router.post("/assignments/{assignment_id}/hand-cash", response_model=StandardResponse, summary="Driver Marks Cash Handed Over to Owner")
async def hand_cash_api(
    assignment_id: str,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db),
):
    res = await notify_cash_handed_service(db, driver, assignment_id)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/assignment/request-return", response_model=StandardResponse, summary="Driver Requests Vehicle Return & Inspection")
async def request_vehicle_return_api(
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    assignment = db.query(DriverBikeAssignment).filter(
        DriverBikeAssignment.driver_user_id == driver.id,
        DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="No active vehicle assignment found.")

    from app.notifications.service import create_notification
    create_notification(
        db,
        assignment.owner_user_id,
        "Vehicle Return Requested",
        f"Driver {driver.email} has requested to return scooty/bike {assignment.bike.bike_name} ({assignment.bike.registration_number}). Please conduct the return inspection to complete deposit refund.",
    )

    return StandardResponse(success=True, message="Return request submitted. Owner has been notified for inspection.")


@router.get("/booking-history", response_model=StandardResponse, summary="Get Driver's Booking Request History")
async def booking_history_api(
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    requests = db.query(BikeBookingRequest).filter(
        BikeBookingRequest.driver_user_id == driver.id
    ).order_by(BikeBookingRequest.created_at.desc()).all()

    data = [
        {
            "id": r.id,
            "bike_id": r.bike_id,
            "bike_name": r.bike.bike_name if r.bike else "Scooty",
            "registration_number": r.bike.registration_number if r.bike else "",
            "status": r.status.value,
            "message": r.message,
            "rental_hours": getattr(r, "rental_hours", 24) or 24,
            "total_amount": float(getattr(r, "total_amount", 0.0) or 0.0),
            "payment_method": getattr(r, "payment_method", "cod") or "cod",
            "cash_received": getattr(r, "cash_received", False) or False,
            "cash_received_at": r.cash_received_at.isoformat() if getattr(r, "cash_received_at", None) else None,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "rejected_reason": r.rejected_reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "daily_rent": float(r.bike.pricing.daily_rent) if r.bike and r.bike.pricing else 500.0,
            "security_deposit": float(r.bike.pricing.security_deposit) if r.bike and r.bike.pricing else 1000.0,
        }
        for r in requests
    ]
    return StandardResponse(success=True, message="Booking history retrieved.", data=data)
