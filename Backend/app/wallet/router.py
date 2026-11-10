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

from app.db.schema import User, WalletTransaction, WalletTxnType, WalletTxnStatus, utcnow
from pydantic import BaseModel, Field

class DirectTopupRequest(BaseModel):
    amount: Decimal = Field(..., ge=500, description="Minimum wallet recharge is ₹500")

router = APIRouter(prefix="/wallet", tags=["Wallet System"])


@router.post("/topup", response_model=StandardResponse, summary="Direct Wallet Top-up (Razorpay / Instant)")
async def direct_wallet_topup_api(
    req: DirectTopupRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wallet = get_or_create_user_wallet(db, user.id)
    wallet.balance += req.amount
    txn = WalletTransaction(
        wallet_id=wallet.id,
        amount=req.amount,
        txn_type=WalletTxnType.RECHARGE,
        status=WalletTxnStatus.SUCCESS,
        reference_id=f"pay_{int(utcnow().timestamp())}",
        description=f"Wallet top-up (Razorpay/Card ₹{req.amount})",
    )
    db.add(txn)
    db.commit()
    db.refresh(wallet)
    return StandardResponse(success=True, message=f"₹{req.amount} credited to your wallet.", data={"balance": float(wallet.balance)})


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
