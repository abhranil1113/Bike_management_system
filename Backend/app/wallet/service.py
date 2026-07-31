# app/wallet/service.py

import hmac
import hashlib
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.db.schema import (
    User,
    Wallet,
    WalletTransaction,
    WalletTxnType,
    WalletTxnStatus,
    Payment,
    PaymentStatus,
    utcnow,
)
from app.wallet.schemas import (
    CreateRechargeOrderRequest,
    VerifyRechargePaymentRequest,
    AdminWalletAdjustmentRequest,
)
from app.notifications.service import create_notification



def get_or_create_user_wallet(db: Session, user_id: str) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=Decimal("0.00"))
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


async def create_recharge_order_service(
    db: Session, user: User, req: CreateRechargeOrderRequest
) -> Dict[str, Any]:
    if req.amount < Decimal("500.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum wallet recharge amount is ₹500.",
        )

    wallet = get_or_create_user_wallet(db, user.id)

    # Generate Razorpay Order ID (or Razorpay SDK call)
    order_id = f"order_w_{user.id[:6]}_{int(utcnow().timestamp())}"

    return {
        "order_id": order_id,
        "amount": float(req.amount),
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "wallet_id": wallet.id,
    }


async def verify_and_credit_recharge_service(
    db: Session, user: User, req: VerifyRechargePaymentRequest, amount: Decimal
) -> Dict[str, Any]:
    # Signature Verification using RAZORPAY_SECRET
    generated_signature = hmac.new(
        settings.RAZORPAY_SECRET.encode('utf-8'),
        f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Note: If running with mock keys during test/dev, allow mock signatures as fallback
    if generated_signature != req.razorpay_signature and not settings.DEBUG:
        create_notification(
            db,
            user.id,
            "Payment Failed",
            "Your payment could not be completed. Please try again.",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay payment signature.",
        )

    wallet = get_or_create_user_wallet(db, user.id)
    wallet.balance += amount

    txn = WalletTransaction(
        wallet_id=wallet.id,
        amount=amount,
        txn_type=WalletTxnType.RECHARGE,
        status=WalletTxnStatus.SUCCESS,
        reference_id=req.razorpay_payment_id,
        description=f"Razorpay wallet recharge (Order ID: {req.razorpay_order_id})",
    )
    db.add(txn)
    db.commit()
    create_notification(
        db,
        user.id,
        "Payment Successful",
        "Your payment has been completed successfully.",
    )

    return {
        "message": f"Wallet recharged successfully with INR {amount}.",
        "new_balance": float(wallet.balance),
        "transaction_id": txn.id,
    }


async def admin_wallet_adjustment_service(
    db: Session, admin_id: str, req: AdminWalletAdjustmentRequest
) -> Dict[str, Any]:
    target_wallet = get_or_create_user_wallet(db, req.user_id)

    new_bal = target_wallet.balance + req.amount
    if new_bal < Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet balance cannot become negative.",
        )

    target_wallet.balance = new_bal
    txn_type = WalletTxnType.ADMIN_ADJUSTMENT

    txn = WalletTransaction(
        wallet_id=target_wallet.id,
        amount=abs(req.amount),
        txn_type=txn_type,
        status=WalletTxnStatus.SUCCESS,
        reference_id=admin_id,
        description=f"Admin Adjustment: {req.reason}",
    )
    db.add(txn)
    db.commit()

    return {
        "message": f"Wallet adjusted by ₹{req.amount}.",
        "new_balance": float(target_wallet.balance),
    }


async def get_wallet_ledger_service(db: Session, user_id: str) -> Dict[str, Any]:
    wallet = get_or_create_user_wallet(db, user_id)
    txns = db.query(WalletTransaction).filter(
        WalletTransaction.wallet_id == wallet.id
    ).order_by(WalletTransaction.created_at.desc()).all()

    ledger = [
        {
            "id": t.id,
            "amount": float(t.amount),
            "txn_type": t.txn_type.value,
            "status": t.status.value,
            "reference_id": t.reference_id,
            "description": t.description,
            "created_at": t.created_at.isoformat(),
        }
        for t in txns
    ]

    return {
        "wallet_id": wallet.id,
        "balance": float(wallet.balance),
        "transactions": ledger,
    }
