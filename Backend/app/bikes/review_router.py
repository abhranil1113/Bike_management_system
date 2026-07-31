# app/bikes/review_router.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.schema import User, Bike, BikeReview, DriverBikeAssignment, AssignmentStatus
from app.api.deps import get_current_user
from app.schemas.auth_schema import StandardResponse

router = APIRouter(prefix="/bikes", tags=["Bike Ratings & Reviews"])


class CreateBikeReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, example=5, description="Rating score from 1 to 5")
    comment: Optional[str] = Field(None, example="Smooth ride and great bike condition!")


@router.post("/{bike_id}/reviews", response_model=StandardResponse, summary="Submit Rating & Review for a Bike")
async def create_bike_review_api(
    bike_id: str,
    req: CreateBikeReviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    review = BikeReview(
        bike_id=bike.id,
        driver_user_id=user.id,
        rating=req.rating,
        comment=req.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return StandardResponse(
        success=True,
        message="Rating & Review submitted successfully.",
        data={
            "review_id": review.id,
            "bike_id": bike.id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat(),
        },
    )


@router.get("/{bike_id}/reviews", response_model=StandardResponse, summary="Get Ratings & Reviews for a Bike")
async def get_bike_reviews_api(
    bike_id: str,
    db: Session = Depends(get_db),
):
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    reviews = db.query(BikeReview).filter(BikeReview.bike_id == bike_id).order_by(BikeReview.created_at.desc()).all()
    avg_rating = db.query(func.avg(BikeReview.rating)).filter(BikeReview.bike_id == bike_id).scalar() or 0.0

    return StandardResponse(
        success=True,
        message="Reviews fetched successfully.",
        data={
            "bike_id": bike_id,
            "total_reviews": len(reviews),
            "average_rating": round(float(avg_rating), 1),
            "reviews": [
                {
                    "id": r.id,
                    "rating": r.rating,
                    "comment": r.comment,
                    "created_at": r.created_at.isoformat(),
                }
                for r in reviews
            ],
        },
    )
