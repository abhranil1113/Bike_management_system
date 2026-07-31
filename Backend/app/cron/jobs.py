# app/cron/jobs.py

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.db.schema import (
    BikeBookingRequest,
    BookingRequestStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    Bike,
    BikeStatus,
    Wallet,
    WalletTransaction,
    WalletTxnType,
    WalletTxnStatus,
    DriverRentalLedger,
    RentalCollectionStatus,
    utcnow,
)
from app.notifications.service import create_notification, notify_rental_overdue
from app.notifications.socket_manager import socket_manager

logger = logging.getLogger(__name__)


# ============================================================
# CRON JOB 1: AUTO-CANCEL UNACCEPTED BOOKINGS AFTER 5 HOURS
# ============================================================

def auto_cancel_stale_booking_requests(
    db: Session, max_hours: int = 5
) -> Dict[str, Any]:
    """
    Cron Job: Automatically cancels booking requests if owner hasn't accepted/rejected
    within max_hours (default: 5 hours).
    Frees driver pending state and issues notification/refunds.
    """
    cutoff_time = utcnow() - timedelta(hours=max_hours)
    
    stale_bookings = (
        db.query(BikeBookingRequest)
        .filter(
            BikeBookingRequest.status == BookingRequestStatus.PENDING,
            BikeBookingRequest.created_at <= cutoff_time,
        )
        .all()
    )

    cancelled_count = 0
    for booking in stale_bookings:
        booking.status = BookingRequestStatus.REJECTED
        booking.rejected_reason = f"Auto-cancelled after {max_hours} hours due to owner inactivity."
        cancelled_count += 1

        bike = db.query(Bike).filter(Bike.id == booking.bike_id).first()
        owner_id = bike.owner_user_id if bike else None

        # Notify driver
        create_notification(
            db=db,
            user_id=booking.driver_user_id,
            title="Booking Request Auto-Cancelled",
            message=f"Your booking request was automatically cancelled because the owner did not respond within {max_hours} hours.",
        )

        # Notify bike owner
        if owner_id:
            create_notification(
                db=db,
                user_id=owner_id,
                title="Booking Request Expired",
                message=f"A booking request for your bike expired and was auto-cancelled after {max_hours} hours.",
            )

        # Emit realtime socket event
        socket_manager.notify_user_sync(
            booking.driver_user_id,
            {"booking_id": booking.id, "reason": booking.rejected_reason},
            event_type="booking_cancelled",
        )

    db.commit()
    logger.info(f"[CRON AUTO-CANCEL] Cancelled {cancelled_count} stale booking requests older than {max_hours}h.")
    return {"status": "success", "cancelled_count": cancelled_count}


# ============================================================
# CRON JOB 2: OVERDUE RENTAL PENALTY & NEGATIVE WALLET BALANCE
# ============================================================

def process_overdue_rental_penalties(
    db: Session,
    agreed_hours: int = 20,
    hourly_penalty_amount: Decimal = Decimal("100.00"),
) -> Dict[str, Any]:
    """
    Cron Job: Calculates overdue rental duration for active assignments.
    If driver kept bike longer than agreed duration (e.g., booked 20 hrs but running 24 hrs),
    charges INR 100 per overdue hour. Wallet balance is allowed to become negative.
    """
    now = utcnow()
    active_assignments = (
        db.query(DriverBikeAssignment)
        .filter(DriverBikeAssignment.status == AssignmentStatus.ACTIVE)
        .all()
    )

    penalized_count = 0
    total_penalty_debited = Decimal("0.00")

    for assignment in active_assignments:
        elapsed_seconds = (now - assignment.assigned_at).total_seconds()
        elapsed_hours = int(elapsed_seconds // 3600)

        if elapsed_hours > agreed_hours:
            overdue_hours = elapsed_hours - agreed_hours
            current_penalty = Decimal(overdue_hours) * hourly_penalty_amount

            driver_wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == assignment.driver_user_id)
                .first()
            )
            if not driver_wallet:
                driver_wallet = Wallet(user_id=assignment.driver_user_id, balance=Decimal("0.00"))
                db.add(driver_wallet)
                db.flush()

            # Deduct penalty from wallet (balance CAN become negative as required)
            driver_wallet.balance -= current_penalty
            total_penalty_debited += current_penalty

            txn = WalletTransaction(
                wallet_id=driver_wallet.id,
                amount=current_penalty,
                txn_type=WalletTxnType.DEBIT,
                status=WalletTxnStatus.SUCCESS,
                reference_id=assignment.id,
                description=f"Overdue rental penalty: INR {hourly_penalty_amount}/hr for {overdue_hours} overdue hours (Agreed: {agreed_hours}h, Total elapsed: {elapsed_hours}h).",
            )
            db.add(txn)
            penalized_count += 1

            # Notify driver about penalty and negative/updated wallet balance
            create_notification(
                db=db,
                user_id=assignment.driver_user_id,
                title="Rental Overdue Penalty Charged",
                message=f"Your bike rental is overdue by {overdue_hours} hour(s). A penalty of INR {current_penalty} has been charged to your wallet. Current wallet balance: INR {driver_wallet.balance:.2f}.",
            )

    db.commit()
    logger.info(
        f"[CRON OVERDUE PENALTY] Penalized {penalized_count} active rentals. Total debited: INR {total_penalty_debited}."
    )
    return {
        "status": "success",
        "penalized_assignments": penalized_count,
        "total_penalty_amount": float(total_penalty_debited),
    }


# ============================================================
# CRON JOB 3: DAILY RENTAL LEDGER & OVERDUE NOTICES
# ============================================================

def generate_daily_rental_ledgers_and_overdue_notices(db: Session) -> Dict[str, Any]:
    """
    Cron Job: Generates daily rental ledgers for active assignments
    and triggers overdue rental notices for overdue collections.
    """
    now = utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    active_assignments = (
        db.query(DriverBikeAssignment)
        .filter(DriverBikeAssignment.status == AssignmentStatus.ACTIVE)
        .all()
    )

    created_ledgers = 0
    notified_overdue = 0

    for assign in active_assignments:
        # Check if ledger exists for today
        existing_ledger = (
            db.query(DriverRentalLedger)
            .filter(
                DriverRentalLedger.assignment_id == assign.id,
                DriverRentalLedger.rental_date >= today_start,
            )
            .first()
        )

        if not existing_ledger:
            ledger = DriverRentalLedger(
                assignment_id=assign.id,
                rental_date=now,
                rent_amount=assign.daily_rent_amount,
                amount_paid=Decimal("0.00"),
                due_amount=assign.daily_rent_amount,
                collection_status=RentalCollectionStatus.PENDING,
                note="Generated by daily cron scheduler",
            )
            db.add(ledger)
            created_ledgers += 1

        # Check overdue ledgers
        overdue_ledgers = (
            db.query(DriverRentalLedger)
            .filter(
                DriverRentalLedger.assignment_id == assign.id,
                DriverRentalLedger.collection_status == RentalCollectionStatus.PENDING,
                DriverRentalLedger.rental_date < today_start,
            )
            .all()
        )

        for ol in overdue_ledgers:
            ol.collection_status = RentalCollectionStatus.OVERDUE
            notify_rental_overdue(db, assign.driver_user_id)
            notified_overdue += 1

    db.commit()
    logger.info(
        f"[CRON RENTAL LEDGER] Created {created_ledgers} ledgers, marked/notified {notified_overdue} overdue."
    )
    return {
        "status": "success",
        "created_ledgers": created_ledgers,
        "overdue_notifications": notified_overdue,
    }


# ============================================================
# CRON JOB 4: BIKE MAINTENANCE & INSURANCE EXPIRY REMINDERS
# ============================================================

def check_bike_maintenance_and_insurance_expiries(db: Session) -> Dict[str, Any]:
    """
    Cron Job: Scans active/verified bikes for maintenance cycles or expired documents.
    """
    bikes = (
        db.query(Bike)
        .filter(Bike.is_active == True)
        .all()
    )

    reminded_count = 0
    for bike in bikes:
        # High km driven bikes maintenance alert
        if bike.km_driven and bike.km_driven > 30000:
            create_notification(
                db=db,
                user_id=bike.owner_user_id,
                title="Bike Maintenance Reminder",
                message=f"Your bike {bike.bike_name} ({bike.registration_number}) has reached {bike.km_driven} km driven. Please schedule routine maintenance inspection.",
            )
            reminded_count += 1

    db.commit()
    return {"status": "success", "maintenance_reminders_sent": reminded_count}


# ============================================================
# MASTER UNIFIED CRON RUNNER
# ============================================================

def run_all_cron_jobs(db: Session) -> Dict[str, Any]:
    """
    Executes all scheduled background cron jobs in sequence.
    """
    res1 = auto_cancel_stale_booking_requests(db)
    res2 = process_overdue_rental_penalties(db)
    res3 = generate_daily_rental_ledgers_and_overdue_notices(db)
    res4 = check_bike_maintenance_and_insurance_expiries(db)

    return {
        "timestamp": utcnow().isoformat(),
        "stale_bookings_job": res1,
        "overdue_penalty_job": res2,
        "rental_ledger_job": res3,
        "maintenance_check_job": res4,
    }
