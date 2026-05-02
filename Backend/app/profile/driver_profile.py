#app/profile/driver_profile.py
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db.schema import DriverProfile, User
from app.api.deps import get_current_user

router = APIRouter(prefix="/driver-profile", tags=["Driver Profile"])


# =========================
# CREATE DRIVER PROFILE
# =========================
@router.post("/")
def create_driver_profile(
    full_name: str = Form(...),
    driving_license_number: Optional[str] = Form(None),
    aadhaar_number: Optional[str] = Form(None),

    emergency_contact_name: Optional[str] = Form(None),
    emergency_contact_phone: Optional[str] = Form(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(DriverProfile).filter_by(user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = DriverProfile(
        user_id=current_user.id,
        full_name=full_name,
        driving_license_number=driving_license_number,
        aadhaar_number=aadhaar_number,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"message": "Driver profile created", "data": profile}

@router.get("/")
def get_driver_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(DriverProfile).filter_by(user_id=current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.patch("/")
def update_driver_profile(
    full_name: Optional[str] = Form(None),
    emergency_contact_name: Optional[str] = Form(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(DriverProfile).filter_by(user_id=current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if full_name:
        profile.full_name = full_name
    if emergency_contact_name:
        profile.emergency_contact_name = emergency_contact_name

    db.commit()
    db.refresh(profile)

    return {"message": "Driver profile updated", "data": profile}