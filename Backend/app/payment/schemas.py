# app/payment/schemas.py

from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentCreateOrderRequest(BaseModel):
    booking_request_id: str = Field(..., description="Target booking request ID")
    amount: Decimal = Field(..., ge=0, example=1500.00)


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(...)
    razorpay_payment_id: str = Field(...)
    razorpay_signature: str = Field(...)
