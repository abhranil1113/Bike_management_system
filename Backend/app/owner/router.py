# app/owner/router.py

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, Bike, BikeBookingRequest
from app.api.deps import get_current_owner
from app.schemas.auth_schema import StandardResponse
from app.owner.schemas import (
    OwnerProfileUpdate,
    BikeCreateRequest,
    BookingDecisionRequest,
    ReturnBikeInspectionRequest,
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
            "security_deposit": float(b.pricing.security_deposit) if b.pricing else 0.0,
        }
        for b in bikes
    ]
    return StandardResponse(success=True, message="Bikes fetched.", data=bike_list)


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
async def return_inspection_api(
    req: ReturnBikeInspectionRequest,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    res = await inspect_and_complete_return_service(db, owner, req)
    return StandardResponse(success=True, message=res["message"], data=res)
