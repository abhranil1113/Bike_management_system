#app/profile/ownerprofile.py
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import shutil
import os

from app.db.database import get_db
from app.db.schema import OwnerProfile, User
from app.api.deps import get_current_user

router = APIRouter(prefix="/owner-profile", tags=["Owner Profile"])

UPLOAD_DIR = "uploads/owner"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# HELPER FUNCTION
# =========================
def save_file(file: UploadFile):
    if not file:
        return None

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


# =========================
# CREATE PROFILE
# =========================
@router.post("/")
def create_owner_profile(
    full_name: str = Form(...),
    phone: str = Form(...),
    business_name: Optional[str] = Form(None),

    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),

    bank_account_name: Optional[str] = Form(None),
    bank_account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),

    address_line_1: Optional[str] = Form(None),
    address_line_2: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),

    profile_picture: Optional[UploadFile] = File(None),
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    passbook_file: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ❗ Prevent duplicate profile
    existing = db.query(OwnerProfile).filter_by(user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Owner profile already exists")

    profile = OwnerProfile(
        user_id=current_user.id,
        full_name=full_name,
        phone=phone,
        business_name=business_name,

        aadhaar_number=aadhaar_number,
        pan_number=pan_number,

        bank_account_name=bank_account_name,
        bank_account_number=bank_account_number,
        ifsc_code=ifsc_code,

        address_line_1=address_line_1,
        address_line_2=address_line_2,
        city=city,
        state=state,
        postal_code=postal_code,

        profile_picture_path=save_file(profile_picture),
        aadhaar_file_path=save_file(aadhaar_file),
        pan_file_path=save_file(pan_file),
        passbook_file_path=save_file(passbook_file),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "message": "Owner profile created successfully",
        "data": profile
    }


# =========================
# GET PROFILE
# =========================
@router.get("/")
def get_owner_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(OwnerProfile).filter_by(user_id=current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# =========================
# UPDATE PROFILE (PATCH)
# =========================
@router.patch("/")
def update_owner_profile(
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    business_name: Optional[str] = Form(None),

    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),

    bank_account_name: Optional[str] = Form(None),
    bank_account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),

    address_line_1: Optional[str] = Form(None),
    address_line_2: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),

    profile_picture: Optional[UploadFile] = File(None),
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    passbook_file: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(OwnerProfile).filter_by(user_id=current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # ✅ Update fields only if provided
    update_data = {
        "full_name": full_name,
        "phone": phone,
        "business_name": business_name,
        "aadhaar_number": aadhaar_number,
        "pan_number": pan_number,
        "bank_account_name": bank_account_name,
        "bank_account_number": bank_account_number,
        "ifsc_code": ifsc_code,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "city": city,
        "state": state,
        "postal_code": postal_code,
    }

    for key, value in update_data.items():
        if value is not None:
            setattr(profile, key, value)

    # ✅ File updates
    if profile_picture:
        profile.profile_picture_path = save_file(profile_picture)

    if aadhaar_file:
        profile.aadhaar_file_path = save_file(aadhaar_file)

    if pan_file:
        profile.pan_file_path = save_file(pan_file)

    if passbook_file:
        profile.passbook_file_path = save_file(passbook_file)

    db.commit()
    db.refresh(profile)

    return {
        "message": "Owner profile updated successfully",
        "data": profile
    }