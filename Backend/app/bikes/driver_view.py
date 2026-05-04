#app/bikes/driver_view.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import (
    Bike,
    BikePricing,
    BikeDocument,
    BikeImage,
    BikeVerificationStatus,
)

router = APIRouter(prefix="/driver/bikes", tags=["Driver - Bike View"])


# =========================================================
# GET ALL VERIFIED BIKES (FOR DRIVER)
# =========================================================

@router.get("/")
def get_available_bikes(
    db: Session = Depends(get_db),
):

    # Only verified & active bikes
    bikes = db.query(Bike).filter(
        Bike.verification_status == BikeVerificationStatus.VERIFIED,
        Bike.is_active == True
    ).all()

    result = []

    for bike in bikes:

        # 🔹 Pricing
        pricing = db.query(BikePricing).filter(
            BikePricing.bike_id == bike.id
        ).first()

        # 🔹 Documents
        documents = db.query(BikeDocument).filter(
            BikeDocument.bike_id == bike.id
        ).first()

        # 🔹 Images (sorted)
        images = db.query(BikeImage).filter(
            BikeImage.bike_id == bike.id
        ).order_by(BikeImage.sort_order).all()

        result.append({
            "bike_id": bike.id,

            # =====================
            # BIKE DETAILS
            # =====================
            "bike_details": {
                "name": bike.bike_name,
                "brand": bike.brand,
                "model": bike.model,
                "registration_number": bike.registration_number,
                "color": bike.color,
                "fuel_type": bike.fuel_type,
                "km_driven": bike.km_driven,
                "year_of_purchase": bike.year_of_purchase,
            },

            # =====================
            # OWNER INFO
            # =====================
            "owner": {
                "owner_id": bike.owner_user_id,
            },

            # =====================
            # PRICING
            # =====================
            "pricing": {
                "daily_rent": pricing.daily_rent if pricing else None,
                "weekly_rent": pricing.weekly_rent if pricing else None,
                "monthly_rent": pricing.monthly_rent if pricing else None,
                "security_deposit": pricing.security_deposit if pricing else None,
            },

            # =====================
            # DOCUMENTS
            # =====================
            "documents": {
                "rc": documents.rc_file_path if documents else None,
                "insurance": documents.insurance_file_path if documents else None,
                "pollution": documents.pollution_file_path if documents else None,
                "permit": documents.permit_file_path if documents else None,
            },

            # =====================
            # IMAGES (SORTED)
            # =====================
            "images": [
                {
                    "url": img.image_path,
                    "type": img.image_type,
                    "order": img.sort_order
                }
                for img in images
            ],
        })

    return {
        "count": len(result),
        "data": result
    }