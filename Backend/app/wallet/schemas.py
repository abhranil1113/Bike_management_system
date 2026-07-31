# app/wallet/schemas.py

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class CreateRechargeOrderRequest(BaseModel):
    amount: Decimal = Field(..., ge=500, description="Minimum wallet recharge amount is ₹500")


class VerifyRechargePaymentRequest(BaseModel):
    razorpay_order_id: str = Field(..., example="order_K9128312")
    razorpay_payment_id: str = Field(..., example="pay_K9128399")
    razorpay_signature: str = Field(..., example="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


class AdminWalletAdjustmentRequest(BaseModel):
    user_id: str = Field(..., description="Target user ID")
    amount: Decimal = Field(..., description="Positive amount to credit, negative to debit")
    reason: str = Field(..., example="Admin manual credit adjustment")


class WalletBalanceResponse(BaseModel):
    wallet_id: str
    user_id: str
    balance: Decimal
