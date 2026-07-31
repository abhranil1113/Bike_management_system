# app/wallet/router.py

from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_user, get_current_admin
from app.schemas.auth_schema import StandardResponse
from app.wallet.schemas import (
    CreateRechargeOrderRequest,
    VerifyRechargePaymentRequest,
    AdminWalletAdjustmentRequest,
)
from app.wallet.service import (
    create_recharge_order_service,
    verify_and_credit_recharge_service,
    admin_wallet_adjustment_service,
    get_wallet_ledger_service,
    get_or_create_user_wallet,
)

router = APIRouter(prefix="/wallet", tags=["Wallet System"])


@router.get("/me", response_model=StandardResponse, summary="Get Current User Wallet Balance & Ledger")
async def get_my_wallet_api(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ledger = await get_wallet_ledger_service(db, user.id)
    return StandardResponse(success=True, message="Wallet retrieved.", data=ledger)


@router.post("/recharge/create-order", response_model=StandardResponse, summary="Create Razorpay Order for Wallet Recharge (Min ₹500)")
async def create_recharge_order_api(
    req: CreateRechargeOrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = await create_recharge_order_service(db, user, req)
    return StandardResponse(success=True, message="Razorpay order created.", data=order)


@router.post("/recharge/verify", response_model=StandardResponse, summary="Verify Razorpay Payment Signature & Credit Wallet")
async def verify_recharge_api(
    req: VerifyRechargePaymentRequest,
    amount: Decimal = Query(..., ge=500, description="Recharge amount"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = await verify_and_credit_recharge_service(db, user, req, amount)
    return StandardResponse(success=True, message=res["message"], data=res)


@router.post("/admin/adjust", response_model=StandardResponse, summary="Admin Adjust User Wallet Balance")
async def admin_wallet_adjust_api(
    req: AdminWalletAdjustmentRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = await admin_wallet_adjustment_service(db, admin.id, req)
    return StandardResponse(success=True, message=res["message"], data=res)
