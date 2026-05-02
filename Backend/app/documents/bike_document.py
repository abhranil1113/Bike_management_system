#app/documents/bike_document.py
import os
import shutil
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import Bike, BikeDocument, User, BikeVerificationStatus
from app.api.deps import get_current_user


router = APIRouter(
    prefix="/bike-documents",
    tags=["Bike Documents"]
)

BASE_DIR = "uploads/bike_documents"
TEMP_DIR = os.path.join(BASE_DIR, "temp")
FINAL_DIR = os.path.join(BASE_DIR, "final")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)


# =========================
# HELPER: SAVE TEMP FILE
# =========================
def save_temp_file(file: UploadFile, bike_id: str, doc_type: str) -> str:
    bike_folder = os.path.join(TEMP_DIR, bike_id)
    os.makedirs(bike_folder, exist_ok=True)

    filename = f"{doc_type}_{datetime.utcnow().timestamp()}_{file.filename}"
    path = os.path.join(bike_folder, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return path


# =========================
# PATCH → UPLOAD (DRAFT)
# =========================
@router.patch("/")
def upload_bike_documents(
    bike_id: str = Form(...),

    rc_file: Optional[UploadFile] = File(None),
    insurance_file: Optional[UploadFile] = File(None),
    pollution_file: Optional[UploadFile] = File(None),
    permit_file: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    # ❌ BLOCK IF LOCKED
    if bike.verification_status in [
        BikeVerificationStatus.PENDING,
        BikeVerificationStatus.VERIFIED
    ]:
        raise HTTPException(400, "Cannot upload in current status")

    # ✅ RESET IF REJECTED
    if bike.verification_status == BikeVerificationStatus.REJECTED:
        bike.verification_status = BikeVerificationStatus.DRAFT

    # SAVE TEMP FILES
    if rc_file:
        save_temp_file(rc_file, bike_id, "rc")

    if insurance_file:
        save_temp_file(insurance_file, bike_id, "insurance")

    if pollution_file:
        save_temp_file(pollution_file, bike_id, "pollution")

    if permit_file:
        save_temp_file(permit_file, bike_id, "permit")

    db.commit()

    return {
        "message": "Files uploaded (draft)",
        "status": bike.verification_status
    }


# =========================
# SUBMIT → FINAL SAVE
# =========================
@router.post("/submit")
def submit_bike_documents(
    bike_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    if bike.verification_status == BikeVerificationStatus.PENDING:
        raise HTTPException(400, "Already submitted")

    if bike.verification_status == BikeVerificationStatus.VERIFIED:
        raise HTTPException(400, "Already verified")

    temp_folder = os.path.join(TEMP_DIR, bike_id)

    if not os.path.exists(temp_folder):
        raise HTTPException(400, "No uploaded files found")

    final_folder = os.path.join(FINAL_DIR, bike_id)
    os.makedirs(final_folder, exist_ok=True)

    final_paths = {}

    # MOVE FILES
    for file_name in os.listdir(temp_folder):
        src = os.path.join(temp_folder, file_name)
        dst = os.path.join(final_folder, file_name)

        shutil.move(src, dst)

        if file_name.startswith("rc_"):
            final_paths["rc"] = dst
        elif file_name.startswith("insurance_"):
            final_paths["insurance"] = dst
        elif file_name.startswith("pollution_"):
            final_paths["pollution"] = dst
        elif file_name.startswith("permit_"):
            final_paths["permit"] = dst

    # CREATE / UPDATE DB
    document = db.query(BikeDocument).filter(
        BikeDocument.bike_id == bike_id
    ).first()

    if not document:
        document = BikeDocument(bike_id=bike_id)

    document.rc_file_path = final_paths.get("rc")
    document.insurance_file_path = final_paths.get("insurance")
    document.pollution_file_path = final_paths.get("pollution")
    document.permit_file_path = final_paths.get("permit")

    bike.verification_status = BikeVerificationStatus.PENDING

    db.add(document)
    db.commit()

    return {
        "message": "Submitted successfully",
        "status": bike.verification_status
    }


# =========================
# GET DOCUMENTS
# =========================
@router.get("/")
def get_bike_documents(
    bike_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        raise HTTPException(404, "Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    document = db.query(BikeDocument).filter(
        BikeDocument.bike_id == bike_id
    ).first()

    if not document:
        return {
            "bike_id": bike_id,
            "status": bike.verification_status,
            "documents": None
        }

    return {
        "bike_id": bike_id,
        "status": bike.verification_status,
        "documents": {
            "rc": document.rc_file_path,
            "insurance": document.insurance_file_path,
            "pollution": document.pollution_file_path,
            "permit": document.permit_file_path
        }
    }