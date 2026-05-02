# app/bikes/bike.py

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db.schema import (
    Bike,
    User,
    FuelType,
    BikeOwnershipType,
    UserRole
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/bikes", tags=["Bikes"])


# =========================
# CREATE BIKE (OWNER)
# =========================
@router.post("/")
def create_bike(
    bike_name: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    registration_number: str = Form(...),
    color: Optional[str] = Form(None),

    fuel_type: FuelType = Form(...),
    ownership_type: BikeOwnershipType = Form(...),

    engine_number: Optional[str] = Form(None),
    chassis_number: Optional[str] = Form(None),

    km_driven: int = Form(0),
    year_of_purchase: Optional[int] = Form(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Correct Enum check
    if current_user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can add bikes")

    # ✅ Validation
    if km_driven < 0:
        raise HTTPException(status_code=400, detail="km_driven cannot be negative")

    # ✅ Check duplicate registration number
    existing = db.query(Bike).filter(
        Bike.registration_number == registration_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Bike already exists")

    bike = Bike(
        owner_user_id=current_user.id,
        bike_name=bike_name,
        brand=brand,
        model=model,
        registration_number=registration_number,
        color=color,
        fuel_type=fuel_type,
        ownership_type=ownership_type,
        engine_number=engine_number,
        chassis_number=chassis_number,
        km_driven=km_driven,
        year_of_purchase=year_of_purchase,
    )

    db.add(bike)
    db.commit()
    db.refresh(bike)

    return {
        "message": "Bike created successfully",
        "bike_id": bike.id
    }


# =========================
# GET ALL BIKES (OWNER)
# =========================
@router.get("/")
def get_my_bikes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bikes = db.query(Bike).filter(
        Bike.owner_user_id == current_user.id
    ).all()

    return bikes


# =========================
# GET SINGLE BIKE
# =========================
@router.get("/{bike_id}")
def get_bike(
    bike_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bike = db.query(Bike).filter(
        Bike.id == bike_id,
        Bike.owner_user_id == current_user.id
    ).first()

    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    return bike


# =========================
# UPDATE BIKE (PATCH)
# =========================
@router.patch("/{bike_id}")
def update_bike(
    bike_id: str,

    bike_name: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    registration_number: Optional[str] = Form(None),
    color: Optional[str] = Form(None),

    fuel_type: Optional[FuelType] = Form(None),
    ownership_type: Optional[BikeOwnershipType] = Form(None),

    engine_number: Optional[str] = Form(None),
    chassis_number: Optional[str] = Form(None),

    km_driven: Optional[int] = Form(None),
    year_of_purchase: Optional[int] = Form(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ Fetch bike with ownership check
    bike = db.query(Bike).filter(
        Bike.id == bike_id,
        Bike.owner_user_id == current_user.id
    ).first()

    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # ✅ Prevent duplicate registration update
    if registration_number:
        existing = db.query(Bike).filter(
            Bike.registration_number == registration_number,
            Bike.id != bike_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Registration number already used"
            )

    # ✅ Validation
    if km_driven is not None and km_driven < 0:
        raise HTTPException(status_code=400, detail="km_driven cannot be negative")

    # ✅ Update fields
    if bike_name is not None:
        bike.bike_name = bike_name
    if brand is not None:
        bike.brand = brand
    if model is not None:
        bike.model = model
    if registration_number is not None:
        bike.registration_number = registration_number
    if color is not None:
        bike.color = color
    if fuel_type is not None:
        bike.fuel_type = fuel_type
    if ownership_type is not None:
        bike.ownership_type = ownership_type
    if engine_number is not None:
        bike.engine_number = engine_number
    if chassis_number is not None:
        bike.chassis_number = chassis_number
    if km_driven is not None:
        bike.km_driven = km_driven
    if year_of_purchase is not None:
        bike.year_of_purchase = year_of_purchase

    db.commit()
    db.refresh(bike)

    return {
        "message": "Bike updated successfully"
    }