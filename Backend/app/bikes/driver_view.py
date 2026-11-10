# app/bikes/driver_view.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.db.schema import (
    Bike,
    BikePricing,
    BikeDocument,
    BikeImage,
    BikeVerificationStatus,
    BikeStatus,
)

router = APIRouter(prefix="/driver/bikes", tags=["Driver - Bike View"])


@router.get("/")
def get_available_bikes(
    search: Optional[str] = Query(None, description="Search term for bike name, brand, or model"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type (petrol, electric, etc.)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum daily rent"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum daily rent"),
    sort_by: Optional[str] = Query("latest", description="Sort by: price_asc, price_desc, latest"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Search, Filter, Sort, and Paginate available bikes for drivers.
    """
    query = db.query(Bike).outerjoin(BikePricing).filter(
        Bike.verification_status == BikeVerificationStatus.VERIFIED,
        Bike.is_active == True,
        Bike.status == BikeStatus.AVAILABLE,
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Bike.bike_name.ilike(search_pattern),
                Bike.brand.ilike(search_pattern),
                Bike.model.ilike(search_pattern),
            )
        )

    if brand:
        query = query.filter(Bike.brand.ilike(f"%{brand}%"))

    if fuel_type:
        query = query.filter(Bike.fuel_type == fuel_type.lower())

    if min_price is not None:
        query = query.filter(BikePricing.daily_rent >= min_price)

    if max_price is not None:
        query = query.filter(BikePricing.daily_rent <= max_price)

    if sort_by == "price_asc":
        query = query.order_by(BikePricing.daily_rent.asc())
    elif sort_by == "price_desc":
        query = query.order_by(BikePricing.daily_rent.desc())
    else:
        query = query.order_by(Bike.created_at.desc())

    total_count = query.count()
    offset = (page - 1) * limit
    bikes = query.offset(offset).limit(limit).all()

    result = []
    for bike in bikes:
        pricing = db.query(BikePricing).filter(BikePricing.bike_id == bike.id).first()
        documents = db.query(BikeDocument).filter(BikeDocument.bike_id == bike.id).first()
        images = (
            db.query(BikeImage)
            .filter(BikeImage.bike_id == bike.id)
            .order_by(BikeImage.sort_order)
            .all()
        )

        result.append({
            "bike_id": bike.id,
            "bike_details": {
                "name": bike.bike_name,
                "brand": bike.brand,
                "model": bike.model,
                "registration_number": bike.registration_number,
                "color": bike.color,
                "fuel_type": bike.fuel_type.value if hasattr(bike.fuel_type, 'value') else str(bike.fuel_type),
                "km_driven": bike.km_driven,
                "year_of_purchase": bike.year_of_purchase,
                "status": bike.status.value if hasattr(bike.status, 'value') else str(bike.status),
            },
            "owner": {
                "owner_id": bike.owner_user_id,
            },
            "pricing": {
                "daily_rent": float(pricing.daily_rent) if pricing else None,
                "hourly_rate": float(pricing.hourly_rate) if (pricing and pricing.hourly_rate) else 100.0,
                "weekly_rent": float(pricing.weekly_rent) if pricing and pricing.weekly_rent else None,
                "monthly_rent": float(pricing.monthly_rent) if pricing and pricing.monthly_rent else None,
                "security_deposit": float(pricing.security_deposit) if pricing else None,
            },
            "tariffs": [
                {"id": t.id, "hours": t.hours, "price": float(t.price)}
                for t in bike.tariffs
            ] if bike.tariffs else [],
            "documents": {
                "rc": documents.rc_file_path if documents else None,
                "insurance": documents.insurance_file_path if documents else None,
                "pollution": documents.pollution_file_path if documents else None,
                "permit": documents.permit_file_path if documents else None,
            },
            "images": [
                {
                    "url": img.image_path,
                    "type": getattr(img, "image_type", None),
                    "order": img.sort_order,
                }
                for img in images
            ],
        })

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "count": len(result),
        "data": result,
    }