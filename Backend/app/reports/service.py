# app/reports/service.py

from typing import Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.schema import Payment, PaymentStatus, PlatformSettings, OwnerPayoutLedger, PayoutStatus


async def generate_revenue_report_service(db: Session) -> Dict[str, Any]:
    tot_rev = db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.SUCCESS).scalar() or Decimal("0.00")
    success_count = db.query(Payment).filter(Payment.status == PaymentStatus.SUCCESS).count()

    settings = db.query(PlatformSettings).first()
    comm_pct = settings.platform_commission_percent if settings else Decimal("10.00")
    tot_comm = (tot_rev * comm_pct) / Decimal("100.00")

    payouts = db.query(func.sum(OwnerPayoutLedger.amount)).filter(OwnerPayoutLedger.payout_status == PayoutStatus.PAID).scalar() or Decimal("0.00")

    return {
        "total_gross_revenue": float(tot_rev),
        "platform_commission_percent": float(comm_pct),
        "total_platform_commission": float(tot_comm),
        "total_owner_payouts": float(payouts),
        "total_successful_payments": success_count,
    }
