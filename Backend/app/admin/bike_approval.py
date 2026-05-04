from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import (
    Bike,
    BikeVerificationStatus,
    BikeDocument,
    BikeImage
)
from app.admin.admin_deps import get_current_admin


router = APIRouter(prefix="/admin/bikes", tags=["Admin - Bike"])


# =========================================================
# BIKE LIST (WITH DOCUMENTS + IMAGES)
# =========================================================

@router.get("/")
def get_all_bikes(
    status: Optional[BikeVerificationStatus] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    query = db.query(Bike).join(Bike.owner)

    if status:
        query = query.filter(Bike.verification_status == status)

    bikes = query.all()

    result = []

    for bike in bikes:

        # Get documents
        documents = db.query(BikeDocument).filter(
            BikeDocument.bike_id == bike.id
        ).first()

        # Get images
        images = db.query(BikeImage).filter(
            BikeImage.bike_id == bike.id
        ).all()

        result.append({
            "bike_id": bike.id,
            "owner_id": bike.owner_user_id,

            "bike_details": {
                "name": bike.bike_name,
                "brand": bike.brand,
                "model": bike.model,
                "registration_number": bike.registration_number,
                "color": bike.color,
                "fuel_type": bike.fuel_type,
                "ownership_type": bike.ownership_type,
                "year_of_purchase": bike.year_of_purchase,
                "km_driven": bike.km_driven,
            },

            "documents": {
                "rc": documents.rc_file_path if documents else None,
                "insurance": documents.insurance_file_path if documents else None,
                "pollution": documents.pollution_file_path if documents else None,
                "permit": documents.permit_file_path if documents else None,
            },

            "images": [
                {
                    "image_url": img.image_path,
                    "type": img.image_type,
                } for img in images
            ],

            "verification_status": bike.verification_status,
        })

    return {
        "count": len(result),
        "data": result
    }


# =========================================================
# BIKE APPROVAL (WITH VALIDATION + REJECTION REASON)
# =========================================================

@router.patch("/{bike_id}")
def approve_bike(
    bike_id: str,
    action: Literal["approve", "reject"] = Query(...),
    reason: Optional[str] = Query(None),

    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):

    bike = db.query(Bike).filter(Bike.id == bike_id).first()

    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # ❗ Reject must have reason
    if action == "reject" and not reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required"
        )

    # Get documents
    documents = db.query(BikeDocument).filter(
        BikeDocument.bike_id == bike.id
    ).first()

    # Get images
    images = db.query(BikeImage).filter(
        BikeImage.bike_id == bike.id
    ).all()

    # ❗ Validate before approval
    if action == "approve":
        if not documents:
            raise HTTPException(400, "Bike documents missing")

        if not images:
            raise HTTPException(400, "Bike images missing")

        if not documents.rc_file_path:
            raise HTTPException(400, "RC document required")

    # Optional: prevent re-approval
    if bike.verification_status == BikeVerificationStatus.VERIFIED:
        raise HTTPException(400, "Bike already verified")

    if action == "approve":
        bike.verification_status = BikeVerificationStatus.VERIFIED

    else:
        bike.verification_status = BikeVerificationStatus.REJECTED
        # NOTE: schema does not have rejection_reason for Bike
        # If you want → add field in schema later

    db.commit()
    db.refresh(bike)

    return {
        "message": f"Bike {action}d successfully",
        "bike_id": bike_id,
        "reason": reason if action == "reject" else None
    }