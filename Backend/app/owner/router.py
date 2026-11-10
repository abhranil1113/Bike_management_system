# app/owner/router.py

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, Bike, BikeBookingRequest, DriverBikeAssignment, AssignmentStatus, DriverProfile, BikeTariff
from app.api.deps import get_current_owner
from app.schemas.auth_schema import StandardResponse
from app.owner.schemas import (
    OwnerProfileUpdate,
    BikeCreateRequest,
    BookingDecisionRequest,
    ReturnBikeInspectionRequest,
    CashStatusUpdateRequest,
    TariffsUpdateRequest,
)
from app.owner.service import (
    update_owner_profile_service,
    upload_owner_documents_service,
    create_bike_listing_service,
    upload_bike_documents_service,
    upload_bike_images_service,
    submit_bike_for_verification,
    handle_booking_request_service,
    inspect_and_complete_return_service,
    update_assignment_cash_status_service,
    get_bike_tariffs_service,
    update_bike_tariffs_service,
)

router = APIRouter(prefix="/owner", tags=["Owner Operations"])


@router.put("/profile", response_model=StandardResponse, summary="Update Owner Profile Details")
async def update_profile_api(
    req: OwnerProfileUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await update_owner_profile_service(db, owner, req)
    return StandardResponse(success=True, message=res["message"])


@router.post("/kyc-documents", response_model=StandardResponse, summary="Upload Owner KYC Documents")
async def upload_kyc_api(
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    passbook_file: Optional[UploadFile] = File(None),
    profile_picture: Optional[UploadFile] = File(None),
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await upload_owner_documents_service(db, owner, aadhaar_file, pan_file, passbook_file, profile_picture)
    return StandardResponse(success=True, message=res["message"])


@router.post("/bikes", response_model=StandardResponse, summary="Create New Bike Listing")
async def create_bike_api(
    req: BikeCreateRequest,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await create_bike_listing_service(db, owner, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/bikes/{bike_id}/documents", response_model=StandardResponse, summary="Upload Bike RC, Insurance, Pollution & Permit")
async def upload_bike_docs_api(
    bike_id: str,
    rc_file: Optional[UploadFile] = File(None),
    insurance_file: Optional[UploadFile] = File(None),
    pollution_file: Optional[UploadFile] = File(None),
    permit_file: Optional[UploadFile] = File(None),
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await upload_bike_documents_service(db, owner, bike_id, rc_file, insurance_file, pollution_file, permit_file)
    return StandardResponse(success=True, message=res["message"])


@router.post("/bikes/{bike_id}/images", response_model=StandardResponse, summary="Upload Multi-Images for Bike")
async def upload_bike_images_api(
    bike_id: str,
    images: List[UploadFile] = File(...),
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await upload_bike_images_service(db, owner, bike_id, images)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/bikes/{bike_id}/submit-verification", response_model=StandardResponse, summary="Submit Bike for Admin Approval")
async def submit_bike_api(
    bike_id: str,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await submit_bike_for_verification(db, owner, bike_id)
    return StandardResponse(success=True, message=res["message"])


@router.get("/bikes", response_model=StandardResponse, summary="List Owner's Bikes")
async def list_owner_bikes_api(
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    bikes = db.query(Bike).filter(Bike.owner_user_id == owner.id).all()
    bike_list = [
        {
            "id": b.id,
            "bike_name": b.bike_name,
            "brand": b.brand,
            "model": b.model,
            "registration_number": b.registration_number,
            "status": b.status.value,
            "verification_status": b.verification_status.value,
            "daily_rent": float(b.pricing.daily_rent) if b.pricing else 0.0,
            "hourly_rate": float(b.pricing.hourly_rate) if (b.pricing and b.pricing.hourly_rate) else 100.0,
            "security_deposit": float(b.pricing.security_deposit) if b.pricing else 0.0,
            "tariffs": [
                {"id": t.id, "hours": t.hours, "price": float(t.price)}
                for t in b.tariffs
            ] if b.tariffs else [],
        }
        for b in bikes
    ]
    return StandardResponse(success=True, message="Bikes fetched.", data=bike_list)


@router.get("/booking-requests", response_model=StandardResponse, summary="List Owner's Incoming Booking Requests")
async def get_owner_booking_requests_api(
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    requests = (
        db.query(BikeBookingRequest)
        .join(Bike, BikeBookingRequest.bike_id == Bike.id)
        .filter(Bike.owner_user_id == owner.id)
        .order_by(BikeBookingRequest.created_at.desc())
        .all()
    )

    data = []
    for r in requests:
        driver_prof = db.query(DriverProfile).filter(DriverProfile.user_id == r.driver_user_id).first()
        pricing = r.bike.pricing if r.bike else None
        data.append({
            "id": r.id,
            "bike_id": r.bike_id,
            "bike_name": r.bike.bike_name if r.bike else "Unknown Bike",
            "registration_number": r.bike.registration_number if r.bike else "",
            "driver_user_id": r.driver_user_id,
            "driver_name": driver_prof.full_name if driver_prof else "Driver",
            "driver_phone": driver_prof.user.phone if driver_prof and driver_prof.user else "",
            "driver_profile_picture": driver_prof.profile_picture_path if driver_prof else None,
            "driver_verification_status": driver_prof.verification_status.value if driver_prof else "draft",
            "driver_emergency_contact": {
                "name": driver_prof.emergency_contact_name,
                "phone": driver_prof.emergency_contact_phone,
            } if driver_prof and driver_prof.emergency_contact_name else None,
            "driver_address": getattr(driver_prof, "address", "") if driver_prof else "",
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "message": r.message,
            "rental_hours": getattr(r, "rental_hours", 24) or 24,
            "total_amount": float(getattr(r, "total_amount", 0.0) or (pricing.daily_rent if pricing else 0.0)),
            "payment_method": getattr(r, "payment_method", "cod") or "cod",
            "cash_received": getattr(r, "cash_received", False) or False,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "rejected_reason": r.rejected_reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "daily_rent": float(pricing.daily_rent) if pricing else 0.0,
            "security_deposit": float(pricing.security_deposit) if pricing else 0.0,
        })
    return StandardResponse(success=True, message="Booking requests fetched.", data=data)


@router.get("/active-rentals", response_model=StandardResponse, summary="List Owner's Active Bike Rentals")
async def get_owner_active_rentals_api(
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    assignments = (
        db.query(DriverBikeAssignment)
        .filter(
            DriverBikeAssignment.owner_user_id == owner.id,
            DriverBikeAssignment.status == AssignmentStatus.ACTIVE,
        )
        .order_by(DriverBikeAssignment.assigned_at.desc())
        .all()
    )

    data = []
    for a in assignments:
        driver_prof = db.query(DriverProfile).filter(DriverProfile.user_id == a.driver_user_id).first()
        data.append({
            "id": a.id,
            "bike_id": a.bike_id,
            "bike_name": a.bike.bike_name if a.bike else "Unknown Bike",
            "registration_number": a.bike.registration_number if a.bike else "",
            "driver_user_id": a.driver_user_id,
            "driver_name": driver_prof.full_name if driver_prof else "Driver",
            "driver_phone": driver_prof.user.phone if driver_prof and driver_prof.user else "",
            "driver_profile_picture": driver_prof.profile_picture_path if driver_prof else None,
            "driver_verification_status": driver_prof.verification_status.value if driver_prof else "draft",
            "driver_emergency_contact": {
                "name": driver_prof.emergency_contact_name,
                "phone": driver_prof.emergency_contact_phone,
            } if driver_prof and driver_prof.emergency_contact_name else None,
            "driver_address": getattr(driver_prof, "address", "") if driver_prof else "",
            "assigned_at": a.assigned_at.isoformat(),
            "daily_rent_amount": float(a.daily_rent_amount),
            "total_rent_amount": float(getattr(a, "total_rent_amount", a.daily_rent_amount) or a.daily_rent_amount),
            "rental_hours": getattr(a, "rental_hours", 24) or 24,
            "payment_method": getattr(a, "payment_method", "cod") or "cod",
            "cash_received": getattr(a, "cash_received", False) or False,
            "cash_received_at": a.cash_received_at.isoformat() if getattr(a, "cash_received_at", None) else None,
            "cod_admin_escalated": getattr(a, "cod_admin_escalated", False) or False,
            "security_deposit_amount": float(a.security_deposit_amount),
            "status": a.status.value,
        })
    return StandardResponse(success=True, message="Active rentals fetched.", data=data)


@router.post("/assignments/{assignment_id}/cash-status", response_model=StandardResponse, summary="Mark COD Cash Payment Received or Not Received")
async def update_cash_status_api(
    assignment_id: str,
    req: CashStatusUpdateRequest,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    res = await update_assignment_cash_status_service(db, owner, assignment_id, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.get("/bikes/{bike_id}/tariffs", response_model=StandardResponse, summary="Get Time-Based Tariffs for a Bike")
async def get_bike_tariffs_api(
    bike_id: str,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    tariffs = await get_bike_tariffs_service(db, owner, bike_id)
    return StandardResponse(success=True, message="Tariffs fetched.", data=tariffs)


@router.post("/bikes/{bike_id}/tariffs", response_model=StandardResponse, summary="Update Time-Based Tariffs for a Bike")
async def update_bike_tariffs_api(
    bike_id: str,
    req: TariffsUpdateRequest,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db),
):
    res = await update_bike_tariffs_service(db, owner, bike_id, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/booking-requests/{booking_id}/decision", response_model=StandardResponse, summary="Accept or Reject Booking Request")
async def booking_decision_api(
    booking_id: str,
    req: BookingDecisionRequest,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await handle_booking_request_service(db, owner, booking_id, req)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/return-inspection", response_model=StandardResponse, summary="Complete Bike Return Inspection & Refund Deposit")
@router.post("/assignments/{assignment_id}/return", response_model=StandardResponse, summary="Complete Return Inspection (Path Param)")
async def return_inspection_api(
    req: ReturnBikeInspectionRequest,
    assignment_id: Optional[str] = None,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    if assignment_id:
        req.assignment_id = assignment_id
    res = await inspect_and_complete_return_service(db, owner, req)
    return StandardResponse(success=True, message=res["message"], data=res)
