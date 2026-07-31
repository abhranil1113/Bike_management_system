# app/reports/service.py

from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.schema import (
    Payment,
    PaymentStatus,
    PlatformSettings,
    OwnerPayoutLedger,
    PayoutStatus,
    BikeBookingRequest,
    BookingRequestStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    DriverRentalLedger,
    RentalCollectionStatus,
    User,
    UserRole,
    utcnow,
)


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


async def generate_analytics_dashboard_service(db: Session) -> Dict[str, Any]:
    """
    Comprehensive Analytics Dashboard:
    Revenue, Owner Earnings, Daily Booking, Monthly Collection, Commission, Active Rentals.
    """
    revenue_data = await generate_revenue_report_service(db)
    
    # Active Rentals & Bookings count
    active_rentals = db.query(DriverBikeAssignment).filter(DriverBikeAssignment.status == AssignmentStatus.ACTIVE).count()
    total_bookings = db.query(BikeBookingRequest).count()
    approved_bookings = db.query(BikeBookingRequest).filter(BikeBookingRequest.status == BookingRequestStatus.APPROVED).count()
    pending_bookings = db.query(BikeBookingRequest).filter(BikeBookingRequest.status == BookingRequestStatus.PENDING).count()

    # Monthly Collections
    now = utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_collection = (
        db.query(func.sum(DriverRentalLedger.amount_paid))
        .filter(DriverRentalLedger.rental_date >= month_start)
        .scalar()
        or Decimal("0.00")
    )

    # Owner Earnings Summary
    owner_count = db.query(User).filter(User.role == UserRole.OWNER).count()
    total_payouts_pending = (
        db.query(func.sum(OwnerPayoutLedger.amount))
        .filter(OwnerPayoutLedger.payout_status == PayoutStatus.PENDING)
        .scalar()
        or Decimal("0.00")
    )

    return {
        "revenue_summary": revenue_data,
        "active_rentals": active_rentals,
        "booking_stats": {
            "total_bookings": total_bookings,
            "approved_bookings": approved_bookings,
            "pending_bookings": pending_bookings,
        },
        "monthly_collection": float(monthly_collection),
        "owner_earnings_summary": {
            "total_owners": owner_count,
            "total_payouts_paid": revenue_data["total_owner_payouts"],
            "total_payouts_pending": float(total_payouts_pending),
        },
    }
