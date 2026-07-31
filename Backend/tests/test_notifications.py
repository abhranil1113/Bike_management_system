# Backend/tests/test_notifications.py

import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_notifications_full_flow():
    suffix = str(uuid.uuid4())[:6]

    print("\n==============================================")
    print(" 1. REGISTER USERS (Admin, Owner, Driver)")
    print("==============================================")
    # Admin
    admin_email = f"admin_notif_{suffix}@example.com"
    admin_phone = f"9001{int(uuid.uuid4())}"[:10]
    admin_reg = client.post("/auth/register", json={
        "full_name": "Admin Notif",
        "email": admin_email,
        "phone": admin_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "admin"
    })
    assert admin_reg.status_code == 200, f"Admin reg failed: {admin_reg.json()}"
    admin_token = admin_reg.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Owner
    owner_email = f"owner_notif_{suffix}@example.com"
    owner_phone = f"9111{int(uuid.uuid4())}"[:10]
    owner_reg = client.post("/auth/register", json={
        "full_name": "Owner Notif",
        "email": owner_email,
        "phone": owner_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "owner"
    })
    assert owner_reg.status_code == 200, f"Owner reg failed: {owner_reg.json()}"
    owner_token = owner_reg.json()["data"]["access_token"]
    owner_id = owner_reg.json()["data"]["user"]["id"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Driver
    driver_email = f"driver_notif_{suffix}@example.com"
    driver_phone = f"9222{int(uuid.uuid4())}"[:10]
    driver_reg = client.post("/auth/register", json={
        "full_name": "Driver Notif",
        "email": driver_email,
        "phone": driver_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "driver"
    })
    assert driver_reg.status_code == 200, f"Driver reg failed: {driver_reg.json()}"
    driver_token = driver_reg.json()["data"]["access_token"]
    driver_id = driver_reg.json()["data"]["user"]["id"]
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    print("\n==============================================")
    print(" 2. TEST OWNER VERIFICATION NOTIFICATIONS")
    print("==============================================")
    # Owner updates profile -> Verification Submitted
    upd_res = client.put("/owner/profile", json={
        "full_name": "Updated Owner Notif",
        "address": "123 Street",
        "city": "Kolkata",
        "state": "West Bengal",
        "pincode": "700001"
    }, headers=owner_headers)
    assert upd_res.status_code == 200

    # Check Owner notification for Verification Submitted
    notifs_res = client.get("/notifications", headers=owner_headers)
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()["data"]["notifications"]
    assert any(n["title"] == "Verification Submitted" for n in notifs)

    # Admin approves Owner -> Verification Approved
    appr_owner = client.post(f"/admin/verify-owner/{owner_id}", json={"approved": True}, headers=admin_headers)
    assert appr_owner.status_code == 200

    notifs_res = client.get("/notifications", headers=owner_headers)
    notifs = notifs_res.json()["data"]["notifications"]
    assert any(n["title"] == "Verification Approved" for n in notifs)

    print("\n==============================================")
    print(" 3. TEST DRIVER VERIFICATION NOTIFICATIONS")
    print("==============================================")
    # Driver updates profile -> Verification Submitted
    d_upd = client.put("/driver/profile", json={
        "full_name": "Updated Driver Notif",
        "address": "456 Avenue"
    }, headers=driver_headers)
    assert d_upd.status_code == 200

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Verification Submitted" for n in d_notifs)

    # Admin approves Driver -> Verification Approved
    appr_driver = client.post(f"/admin/verify-driver/{driver_id}", json={"approved": True}, headers=admin_headers)
    assert appr_driver.status_code == 200

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Verification Approved" for n in d_notifs)

    print("\n==============================================")
    print(" 4. TEST BIKE VERIFICATION NOTIFICATIONS")
    print("==============================================")
    # Owner creates Bike & Submits
    b_res = client.post("/owner/bikes", json={
        "bike_name": "Royal Enfield 350",
        "brand": "Royal Enfield",
        "model": "Classic 350",
        "registration_number": f"WB04{suffix.upper()}",
        "color": "Black",
        "fuel_type": "petrol",
        "ownership_type": "self",
        "daily_rent": 800.0,
        "security_deposit": 2000.0,
    }, headers=owner_headers)
    bike_id = b_res.json()["data"]["bike_id"]

    sub_res = client.post(f"/owner/bikes/{bike_id}/submit-verification", headers=owner_headers)
    assert sub_res.status_code == 200

    notifs = client.get("/notifications", headers=owner_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Bike Submitted" for n in notifs)

    # Admin approves Bike -> Bike Approved
    appr_bike = client.post(f"/admin/verify-bike/{bike_id}", json={"approved": True}, headers=admin_headers)
    assert appr_bike.status_code == 200

    notifs = client.get("/notifications", headers=owner_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Bike Approved" for n in notifs)

    print("\n==============================================")
    print(" 5. TEST BOOKING & ASSIGNMENT NOTIFICATIONS")
    print("==============================================")
    # Driver recharges wallet
    client.post(f"/wallet/recharge/verify?amount=3000.0", json={
        "razorpay_order_id": f"order_{suffix}",
        "razorpay_payment_id": f"pay_{suffix}",
        "razorpay_signature": "mock_sig",
    }, headers=driver_headers)

    # Driver requests booking -> Notify Owner (New Booking Request)
    book_req = client.post("/driver/bookings", json={"bike_id": bike_id, "message": "Test booking"}, headers=driver_headers)
    assert book_req.status_code == 200
    booking_id = book_req.json()["data"]["booking_id"]

    o_notifs = client.get("/notifications", headers=owner_headers).json()["data"]["notifications"]
    assert any(n["title"] == "New Booking Request" for n in o_notifs)

    # Owner approves booking -> Notify Driver (Booking Approved & Bike Assigned)
    dec_res = client.post(f"/owner/booking-requests/{booking_id}/decision", json={"accepted": True}, headers=owner_headers)
    assert dec_res.status_code == 200
    assignment_id = dec_res.json()["data"]["assignment_id"]

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Booking Approved" for n in d_notifs)
    assert any(n["title"] == "Bike Assigned" for n in d_notifs)

    # Return bike -> Notify Driver (Assignment Ended)
    ret_res = client.post("/owner/return-inspection", json={
        "assignment_id": assignment_id,
        "is_damaged": False,
        "damage_charge": 0.0,
        "notes": "All good"
    }, headers=owner_headers)
    assert ret_res.status_code == 200

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Assignment Ended" for n in d_notifs)

    print("\n==============================================")
    print(" 6. TEST SUPPORT TICKET NOTIFICATIONS")
    print("==============================================")
    supp_res = client.post("/support/tickets", json={
        "subject": "Need help with app",
        "description": "Issue with app loading"
    }, headers=driver_headers)
    assert supp_res.status_code == 200
    ticket_id = supp_res.json()["data"]["ticket_id"]

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Support Ticket Created" for n in d_notifs)

    # Resolve support ticket
    res_ticket = client.post("/support/admin/resolve", json={
        "ticket_id": ticket_id,
        "status": "resolved"
    }, headers=admin_headers)
    assert res_ticket.status_code == 200

    d_notifs = client.get("/notifications", headers=driver_headers).json()["data"]["notifications"]
    assert any(n["title"] == "Support Ticket Resolved" for n in d_notifs)

    print("\n==============================================")
    print(" 7. TEST NOTIFICATION REST APIs (READ, UNREAD COUNT, DELETE)")
    print("==============================================")
    # Unread count
    uc_res = client.get("/notifications/unread-count", headers=driver_headers)
    assert uc_res.status_code == 200
    unread_count = uc_res.json()["data"]["unread_count"]
    assert unread_count > 0

    # Mark single read
    target_notif = d_notifs[0]
    notif_id = target_notif["id"]
    read_res = client.patch(f"/notifications/{notif_id}/read", headers=driver_headers)
    assert read_res.status_code == 200

    # Mark all read
    read_all_res = client.patch("/notifications/read-all", headers=driver_headers)
    assert read_all_res.status_code == 200

    uc_res2 = client.get("/notifications/unread-count", headers=driver_headers)
    assert uc_res2.json()["data"]["unread_count"] == 0

    # Delete single notification
    del_res = client.delete(f"/notifications/{notif_id}", headers=driver_headers)
    assert del_res.status_code == 200

    print("\n[SUCCESS] ALL NOTIFICATION TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_notifications_full_flow()
