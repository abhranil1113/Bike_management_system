# app/payment/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_user
from app.schemas.auth_schema import StandardResponse
from app.payment.schemas import PaymentCreateOrderRequest, PaymentVerifyRequest
from app.payment.service import (
    create_booking_payment_order_service,
    verify_booking_payment_service,
)

router = APIRouter(prefix="/payments", tags=["Payment System"])


@router.post("/create-order", response_model=StandardResponse, summary="Create Razorpay Order for Booking")
async def create_order_api(
    req: PaymentCreateOrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = await create_booking_payment_order_service(db, user, req)
    return StandardResponse(success=True, message="Order created.", data=res)


@router.post("/verify-signature", response_model=StandardResponse, summary="Verify Razorpay Payment Signature")
async def verify_signature_api(
    req: PaymentVerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = await verify_booking_payment_service(db, user, req)
    return StandardResponse(success=True, message=res["message"], data=res)
