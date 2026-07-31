# Backend/tests/test_cron_jobs.py

import os
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from app.db.database import SessionLocal
from app.db.schema import (
    User,
    OwnerProfile,
    DriverProfile,
    OwnerVerificationStatus,
    DriverVerificationStatus,
    Bike,
    BikeStatus,
    BikeVerificationStatus,
    BikeBookingRequest,
    BookingRequestStatus,
    DriverBikeAssignment,
    AssignmentStatus,
    Wallet,
    WalletTransaction,
    utcnow,
)
from app.cron.jobs import (
    auto_cancel_stale_booking_requests,
    process_overdue_rental_penalties,
    generate_daily_rental_ledgers_and_overdue_notices,
    check_bike_maintenance_and_insurance_expiries,
    run_all_cron_jobs,
)

client = TestClient(app)


def test_cron_jobs_and_negative_wallet_balance():
    suffix = str(uuid.uuid4())[:6]

    print("\n==============================================")
    print(" 1. ADMIN USER SETUP")
    print("==============================================")
    admin_email = f"admin_cron_{suffix}@example.com"
    admin_phone = f"9009{int(uuid.uuid4())}"[:10]
    admin_reg = client.post("/auth/register", json={
        "full_name": "Admin Cron",
        "email": admin_email,
        "phone": admin_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "admin"
    })
    assert admin_reg.status_code == 200
    admin_token = admin_reg.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("\n==============================================")
    print(" 2. SETUP OWNER, DRIVER, BIKE & STALE BOOKING")
    print("==============================================")
    owner_email = f"owner_cron_{suffix}@example.com"
    owner_phone = f"9119{int(uuid.uuid4())}"[:10]
    owner_reg = client.post("/auth/register", json={
        "full_name": "Owner Cron",
        "email": owner_email,
        "phone": owner_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "owner"
    })
    owner_token = owner_reg.json()["data"]["access_token"]
    owner_id = owner_reg.json()["data"]["user"]["id"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Verify Owner
    client.post(f"/admin/verify-owner/{owner_id}", json={"approved": True}, headers=admin_headers)

    # Create Bike
    b_res = client.post("/owner/bikes", json={
        "bike_name": "KTM Duke 250",
        "brand": "KTM",
        "model": "Duke 250",
        "registration_number": f"WB06{suffix.upper()}",
        "color": "Orange",
        "fuel_type": "petrol",
        "ownership_type": "self",
        "daily_rent": 1000.0,
        "security_deposit": 2000.0,
    }, headers=owner_headers)
    bike_id = b_res.json()["data"]["bike_id"]

    # Verify Bike
    client.post(f"/admin/verify-bike/{bike_id}", json={"approved": True}, headers=admin_headers)

    # Driver Setup
    driver_email = f"driver_cron_{suffix}@example.com"
    driver_phone = f"9229{int(uuid.uuid4())}"[:10]
    driver_reg = client.post("/auth/register", json={
        "full_name": "Driver Cron",
        "email": driver_email,
        "phone": driver_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "driver"
    })
    driver_token = driver_reg.json()["data"]["access_token"]
    driver_id = driver_reg.json()["data"]["user"]["id"]
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    # Verify Driver
    client.post(f"/admin/verify-driver/{driver_id}", json={"approved": True}, headers=admin_headers)

    db = SessionLocal()
    try:
        # Create a stale booking request created 6 hours ago
        stale_time = utcnow() - timedelta(hours=6)
        stale_booking = BikeBookingRequest(
            driver_user_id=driver_id,
            bike_id=bike_id,
            status=BookingRequestStatus.PENDING,
            message="Booking created 6 hours ago",
            created_at=stale_time,
        )
        db.add(stale_booking)
        db.commit()
        db.refresh(stale_booking)
        stale_id = stale_booking.id

        print("\n==============================================")
        print(" 3. TEST CRON JOB 1: STALE BOOKING AUTO-CANCEL")
        print("==============================================")
        res_stale = auto_cancel_stale_booking_requests(db, max_hours=5)
        assert res_stale["cancelled_count"] >= 1, "Stale booking was not auto-cancelled!"

        refreshed_booking = db.query(BikeBookingRequest).filter(BikeBookingRequest.id == stale_id).first()
        assert refreshed_booking.status == BookingRequestStatus.REJECTED
        assert "Auto-cancelled after 5 hours" in refreshed_booking.rejected_reason
        print("[PASS] Stale booking created 6h ago auto-cancelled successfully.")

        print("\n==============================================")
        print(" 4. TEST CRON JOB 2: OVERDUE PENALTY & NEGATIVE WALLET BALANCE")
        print("==============================================")
        # Create active assignment started 24 hours ago (agreed 20 hrs -> 4 hours overdue)
        assigned_24h_ago = utcnow() - timedelta(hours=24)
        assignment = DriverBikeAssignment(
            driver_user_id=driver_id,
            owner_user_id=owner_id,
            bike_id=bike_id,
            daily_rent_amount=Decimal("1000.00"),
            security_deposit_amount=Decimal("2000.00"),
            status=AssignmentStatus.ACTIVE,
            assigned_at=assigned_24h_ago,
        )
        db.add(assignment)

        # Set driver wallet balance to low amount (e.g. INR 50.00) to test negative balance after penalty
        driver_wallet = db.query(Wallet).filter(Wallet.user_id == driver_id).first()
        if not driver_wallet:
            driver_wallet = Wallet(user_id=driver_id, balance=Decimal("50.00"))
            db.add(driver_wallet)
        else:
            driver_wallet.balance = Decimal("50.00")
        db.commit()

        # Run process_overdue_rental_penalties (4 hours overdue * INR 100/hr = INR 400 penalty)
        res_penalty = process_overdue_rental_penalties(db, agreed_hours=20, hourly_penalty_amount=Decimal("100.00"))
        assert res_penalty["penalized_assignments"] >= 1
        assert res_penalty["total_penalty_amount"] >= 400.0

        # Check driver wallet balance -> INR 50 - INR 400 = -INR 350 (NEGATIVE BALANCE)
        db.refresh(driver_wallet)
        assert driver_wallet.balance < Decimal("0.00"), f"Wallet balance is not negative: {driver_wallet.balance}"
        print(f"[PASS] Overdue rental penalty debited INR 400. Wallet balance became NEGATIVE: INR {driver_wallet.balance:.2f}")

        print("\n==============================================")
        print(" 5. TEST CRON JOB 3 & ADMIN REST API")
        print("==============================================")
        run_res = client.post("/admin/cron/run", headers=admin_headers)
        assert run_res.status_code == 200, f"Cron trigger failed: {run_res.json()}"
        assert run_res.json()["data"]["stale_bookings_job"]["status"] == "success"

        status_res = client.get("/admin/cron/status", headers=admin_headers)
        assert status_res.status_code == 200
        assert isinstance(status_res.json()["data"]["scheduler_running"], bool)
        print("[PASS] Admin Cron REST APIs verified successfully.")

        print("\n==============================================")
        print(" 6. TEST ANALYTICS DASHBOARD API")
        print("==============================================")
        dash_res = client.get("/reports/dashboard", headers=admin_headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()["data"]
        assert "revenue_summary" in dash_data
        assert "active_rentals" in dash_data
        print("[PASS] Master Analytics Dashboard API verified.")

        print("\n[SUCCESS] ALL CRON JOBS AND NEGATIVE WALLET BALANCE TESTS PASSED CLEANLY!")
    finally:
        db.close()


if __name__ == "__main__":
    test_cron_jobs_and_negative_wallet_balance()
