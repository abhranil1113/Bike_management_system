# app/driver/router.py

from typing import Optional, List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, DriverBikeAssignment, BikeBookingRequest, BookingRequestStatus, AssignmentStatus
from app.api.deps import get_current_driver
from app.schemas.auth_schema import StandardResponse
from app.driver.schemas import DriverProfileUpdate, BikeSearchQuery, CreateBookingRequest
from app.driver.service import (
    update_driver_profile_service,
    upload_driver_documents_service,
    search_available_bikes_service,
    request_bike_booking_service,
)

router = APIRouter(prefix="/driver", tags=["Driver Operations"])


@router.put("/profile", response_model=StandardResponse, summary="Update Driver Profile Details")
async def update_profile_api(
    req: DriverProfileUpdate,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    res = await update_driver_profile_service(db, driver, req)
    return StandardResponse(success=True, message=res["message"])


@router.post("/kyc-documents", response_model=StandardResponse, summary="Upload Driver Driving License & Aadhaar")
async def upload_kyc_api(
    license_file: Optional[UploadFile] = File(None),
    aadhaar_file: Optional[UploadFile] = File(None),
    profile_picture: Optional[UploadFile] = File(None),
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    res = await upload_driver_documents_service(db, driver, license_file, aadhaar_file, profile_picture)
    return StandardResponse(success=True, message=res["message"])


@router.post("/bikes/search", response_model=StandardResponse, summary="Search Available Verified Bikes")
async def search_bikes_api(
    query: BikeSearchQuery,
    driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    bikes = await search_available_bikes_service(db, query)
    return StandardResponse(success=True, message=f"Found {len(bikes)} available bikes.", data=bikes)


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

    booking.status = BookingRequestStatus.REJECTED
    booking.rejected_reason = "Cancelled by driver."
    db.commit()

    return StandardResponse(success=True, message="Booking request cancelled successfully.")


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
        "security_deposit": float(assignment.security_deposit_amount),
        "status": assignment.status.value,
    }
    return StandardResponse(success=True, message="Active assignment retrieved.", data=data)


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
            "bike_name": r.bike.bike_name,
            "status": r.status.value,
            "message": r.message,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "rejected_reason": r.rejected_reason,
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]
    return StandardResponse(success=True, message="Booking history retrieved.", data=data)
