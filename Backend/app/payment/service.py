# app/payment/service.py

import hmac
import hashlib
from typing import Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.db.schema import User, Payment, PaymentStatus, BikeBookingRequest, utcnow
from app.payment.schemas import PaymentCreateOrderRequest, PaymentVerifyRequest
from app.notifications.service import create_notification



async def create_booking_payment_order_service(
    db: Session, user: User, req: PaymentCreateOrderRequest
) -> Dict[str, Any]:
    booking = db.query(BikeBookingRequest).filter(
        BikeBookingRequest.id == req.booking_request_id,
        BikeBookingRequest.driver_user_id == user.id,
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking request not found")

    order_id = f"order_b_{booking.id[:6]}_{int(utcnow().timestamp())}"

    payment = Payment(
        booking_request_id=booking.id,
        driver_user_id=user.id,
        amount=req.amount,
        currency="INR",
        razorpay_order_id=order_id,
        status=PaymentStatus.CREATED,
    )
    db.add(payment)
    db.commit()

    return {
        "order_id": order_id,
        "amount": float(req.amount),
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    }


async def verify_booking_payment_service(
    db: Session, user: User, req: PaymentVerifyRequest
) -> Dict[str, Any]:
    payment = db.query(Payment).filter(
        Payment.razorpay_order_id == req.razorpay_order_id,
        Payment.driver_user_id == user.id,
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")

    # Signature verification
    generated_sig = hmac.new(
        settings.RAZORPAY_SECRET.encode('utf-8'),
        f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if generated_sig != req.razorpay_signature and not settings.DEBUG:
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = "Signature verification failed"
        db.commit()
        create_notification(
            db,
            user.id,
            "Payment Failed",
            "Your payment could not be completed. Please try again.",
        )
        raise HTTPException(status_code=400, detail="Razorpay signature verification failed")

    payment.razorpay_payment_id = req.razorpay_payment_id
    payment.status = PaymentStatus.SUCCESS
    payment.paid_at = utcnow()

    db.commit()
    create_notification(
        db,
        user.id,
        "Payment Successful",
        "Your payment has been completed successfully.",
    )
    return {"message": "Payment verified successfully.", "payment_id": payment.id}
