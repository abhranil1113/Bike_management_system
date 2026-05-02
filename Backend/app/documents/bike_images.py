#app/documents/bike_images.py
import os
import shutil
from uuid import uuid4
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import BikeImage, Bike, UserRole
from app.api.deps import get_current_user

router = APIRouter(prefix="/bike-images", tags=["Bike Images"])


# =========================
# CONFIG
# =========================
UPLOAD_DIR = "uploads/bike_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# POST - UPLOAD BIKE IMAGE
# =========================
@router.post("/")
def upload_bike_image(
    bike_id: str = Form(...),
    image: UploadFile = File(...),
    image_type: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(1),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 🔒 Only OWNER allowed
    if current_user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can upload bike images")

    # ✅ Check bike exists
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # 🔒 Ownership check
    if bike.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your bike")

    # ✅ Save file
    file_ext = image.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # ✅ Save to DB
    bike_image = BikeImage(
        bike_id=bike_id,
        image_path=file_path,
        image_type=image_type,
        sort_order=sort_order or 1,
    )

    db.add(bike_image)
    db.commit()
    db.refresh(bike_image)

    return {
        "message": "Bike image uploaded successfully",
        "data": {
            "id": bike_image.id,
            "bike_id": bike_image.bike_id,
            "image_path": bike_image.image_path,
            "image_type": bike_image.image_type,
            "sort_order": bike_image.sort_order,
        },
    }


# =========================
# GET - FETCH BIKE IMAGES
# =========================
@router.get("/{bike_id}")
def get_bike_images(
    bike_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 🔒 Only OWNER allowed
    if current_user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can view bike images")

    # ✅ Check bike exists
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # 🔒 Ownership check
    if bike.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your bike")

    images = (
        db.query(BikeImage)
        .filter(BikeImage.bike_id == bike_id)
        .order_by(BikeImage.sort_order.asc())
        .all()
    )

    return {
        "bike_id": bike_id,
        "total_images": len(images),
        "images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "image_type": img.image_type,
                "sort_order": img.sort_order,
            }
            for img in images
        ],
    }