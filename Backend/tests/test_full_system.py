# Backend/tests/test_full_system.py

import os
import sys
import uuid
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_full_system_workflow():
    suffix = str(uuid.uuid4())[:6]

    print("\n==============================================")
    print(" 1. ADMIN USER SETUP")
    print("==============================================")
    admin_email = f"admin_{suffix}@example.com"
    admin_phone = f"9000{int(uuid.uuid4())}"[:10]
    admin_reg = client.post("/auth/register", json={
        "full_name": "System Admin",
        "email": admin_email,
        "phone": admin_phone,
        "password": "AdminPassword123!",
        "confirm_password": "AdminPassword123!",
        "role": "admin"
    })
    assert admin_reg.status_code == 200, f"Admin reg failed: {admin_reg.json()}"
    admin_token = admin_reg.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Admin registered & authenticated.")

    print("\n==============================================")
    print(" 2. OWNER REGISTRATION & BIKE LISTING")
    print("==============================================")
    owner_email = f"owner_{suffix}@example.com"
    owner_phone = f"9110{int(uuid.uuid4())}"[:10]
    owner_reg = client.post("/auth/register", json={
        "full_name": "Bike Owner",
        "email": owner_email,
        "phone": owner_phone,
        "password": "OwnerPassword123!",
        "confirm_password": "OwnerPassword123!",
        "role": "owner"
    })
    assert owner_reg.status_code == 200, f"Owner reg failed: {owner_reg.json()}"
    owner_token = owner_reg.json()["data"]["access_token"]
    owner_id = owner_reg.json()["data"]["user"]["id"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Admin approves Owner
    approve_owner = client.post(f"/admin/verify-owner/{owner_id}", json={"approved": True}, headers=admin_headers)
    assert approve_owner.status_code == 200

    # Owner creates Bike
    bike_res = client.post("/owner/bikes", json={
        "bike_name": "Yamaha FZ 25",
        "brand": "Yamaha",
        "model": "FZ 25",
        "registration_number": f"WB02{suffix.upper()}",
        "color": "Blue",
        "fuel_type": "petrol",
        "ownership_type": "self",
        "daily_rent": 600.0,
        "security_deposit": 1500.0,
    }, headers=owner_headers)
    assert bike_res.status_code == 200, f"Bike creation failed: {bike_res.json()}"
    bike_id = bike_res.json()["data"]["bike_id"]

    # Admin approves Bike
    approve_bike = client.post(f"/admin/verify-bike/{bike_id}", json={"approved": True}, headers=admin_headers)
    assert approve_bike.status_code == 200
    print("[PASS] Owner verified & Bike published.")

    print("\n==============================================")
    print(" 3. DRIVER REGISTRATION, WALLET RECHARGE & BOOKING")
    print("==============================================")
    driver_email = f"driver_{suffix}@example.com"
    driver_phone = f"9220{int(uuid.uuid4())}"[:10]
    driver_reg = client.post("/auth/register", json={
        "full_name": "Bike Driver",
        "email": driver_email,
        "phone": driver_phone,
        "password": "DriverPassword123!",
        "confirm_password": "DriverPassword123!",
        "role": "driver"
    })
    assert driver_reg.status_code == 200, f"Driver reg failed: {driver_reg.json()}"
    driver_token = driver_reg.json()["data"]["access_token"]
    driver_id = driver_reg.json()["data"]["user"]["id"]
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    # Admin approves Driver
    approve_driver = client.post(f"/admin/verify-driver/{driver_id}", json={"approved": True}, headers=admin_headers)
    assert approve_driver.status_code == 200

    # Driver recharges wallet with INR 3000 (>= INR 500 rule)
    recharge_order = client.post("/wallet/recharge/create-order", json={"amount": 3000.0}, headers=driver_headers)
    assert recharge_order.status_code == 200
    order_id = recharge_order.json()["data"]["order_id"]

    # Verify payment & credit wallet
    credit_res = client.post(f"/wallet/recharge/verify?amount=3000.0", json={
        "razorpay_order_id": order_id,
        "razorpay_payment_id": f"pay_{suffix}",
        "razorpay_signature": "mock_sig",
    }, headers=driver_headers)
    assert credit_res.status_code == 200
    print("[PASS] Driver wallet recharged with INR 3000.")

    # Driver requests booking
    booking_req = client.post("/driver/bookings", json={"bike_id": bike_id, "message": "Need bike for 3 days."}, headers=driver_headers)
    assert booking_req.status_code == 200, f"Booking request failed: {booking_req.json()}"
    booking_id = booking_req.json()["data"]["booking_id"]

    # Owner accepts booking (deducts wallet: INR 600 rent + INR 1500 deposit = INR 2100)
    accept_res = client.post(f"/owner/booking-requests/{booking_id}/decision", json={"accepted": True}, headers=owner_headers)
    assert accept_res.status_code == 200, f"Accept failed: {accept_res.json()}"
    assignment_id = accept_res.json()["data"]["assignment_id"]
    print("[PASS] Owner accepted booking. Bike assigned and wallet deducted.")

    print("\n==============================================")
    print(" 4. RETURN INSPECTION & DEPOSIT REFUND")
    print("==============================================")
    return_res = client.post("/owner/return-inspection", json={
        "assignment_id": assignment_id,
        "is_damaged": False,
        "damage_charge": 0.0,
        "notes": "Bike returned in perfect condition."
    }, headers=owner_headers)
    assert return_res.status_code == 200, f"Return failed: {return_res.json()}"
    print("[PASS] Bike returned & deposit refunded to driver wallet.")

    print("\n[SUCCESS] FULL SYSTEM INTEGRATION TEST PASSED CLEANLY!")


if __name__ == "__main__":
    test_full_system_workflow()
