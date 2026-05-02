# app/bikes/bike_price.py

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import Bike, BikePricing, User
from app.api.deps import get_current_user


router = APIRouter(
    prefix="/bike-pricing",
    tags=["Bike Pricing"]
)


# ============================================================
# CREATE BIKE PRICING (POST)
# ============================================================
@router.post("/")
def create_bike_pricing(
    bike_id: str = Query(...),
    daily_rent: Decimal = Query(...),
    security_deposit: Decimal = Query(...),
    weekly_rent: Optional[Decimal] = Query(None),
    monthly_rent: Optional[Decimal] = Query(None),
    late_fee_per_day: Optional[Decimal] = Query(Decimal("0.00")),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Owner sets pricing for a bike
    """

    # Check bike exists
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # Check ownership
    if bike.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if pricing already exists
    existing_pricing = db.query(BikePricing).filter(
        BikePricing.bike_id == bike_id
    ).first()

    if existing_pricing:
        raise HTTPException(
            status_code=400,
            detail="Pricing already exists for this bike"
        )

    # Create pricing
    pricing = BikePricing(
        bike_id=bike_id,
        daily_rent=daily_rent,
        weekly_rent=weekly_rent,
        monthly_rent=monthly_rent,
        security_deposit=security_deposit,
        late_fee_per_day=late_fee_per_day,
    )

    db.add(pricing)
    db.commit()
    db.refresh(pricing)

    return {
        "message": "Bike pricing created successfully",
        "data": pricing
    }


# ============================================================
# GET BIKE PRICING (GET)
# ============================================================
@router.get("/")
def get_bike_pricing(
    bike_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get pricing for a specific bike
    """

    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # Only owner can view (you can later relax this for drivers)
    if bike.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    pricing = db.query(BikePricing).filter(
        BikePricing.bike_id == bike_id
    ).first()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing not found")

    return {
        "message": "Bike pricing fetched successfully",
        "data": pricing
    }


# ============================================================
# UPDATE BIKE PRICING (PATCH)
# ============================================================
@router.patch("/")
def update_bike_pricing(
    bike_id: str = Query(...),
    daily_rent: Optional[Decimal] = Query(None),
    weekly_rent: Optional[Decimal] = Query(None),
    monthly_rent: Optional[Decimal] = Query(None),
    security_deposit: Optional[Decimal] = Query(None),
    late_fee_per_day: Optional[Decimal] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update bike pricing
    """

    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    if bike.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    pricing = db.query(BikePricing).filter(
        BikePricing.bike_id == bike_id
    ).first()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing not found")

    # Update only provided fields
    if daily_rent is not None:
        pricing.daily_rent = daily_rent

    if weekly_rent is not None:
        pricing.weekly_rent = weekly_rent

    if monthly_rent is not None:
        pricing.monthly_rent = monthly_rent

    if security_deposit is not None:
        pricing.security_deposit = security_deposit

    if late_fee_per_day is not None:
        pricing.late_fee_per_day = late_fee_per_day

    db.commit()
    db.refresh(pricing)

    return {
        "message": "Bike pricing updated successfully",
        "data": pricing
    }