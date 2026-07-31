# Backend/tests/test_auth.py

import os
import sys
import uuid

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_auth_flow():
    unique_suffix = str(uuid.uuid4())[:8]
    test_email = f"driver_{unique_suffix}@example.com"
    test_phone = f"99{unique_suffix[:8]}"

    print("\n--- Testing Registration ---")
    reg_payload = {
        "full_name": "Test Driver",
        "email": test_email,
        "phone": test_phone,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "driver"
    }
    response = client.post("/auth/register", json=reg_payload)
    print("Register Status:", response.status_code)
    print("Register Response:", response.json())
    assert response.status_code == 200, f"Register failed: {response.json()}"
    res_data = response.json()["data"]
    access_token = res_data["access_token"]
    refresh_token = res_data["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None

    print("\n--- Testing Login ---")
    login_payload = {
        "email": test_email,
        "password": "Password123!"
    }
    login_res = client.post("/auth/login", json=login_payload)
    print("Login Status:", login_res.status_code)
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"
    login_data = login_res.json()["data"]
    assert login_data["user"]["email"] == test_email

    print("\n--- Testing Refresh Token ---")
    refresh_res = client.post("/auth/refresh-token", json={"refresh_token": refresh_token})
    print("Refresh Status:", refresh_res.status_code)
    assert refresh_res.status_code == 200, f"Refresh failed: {refresh_res.json()}"
    new_access_token = refresh_res.json()["data"]["access_token"]
    assert new_access_token is not None

    print("\n--- Testing Get Me ---")
    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    print("Get Me Status:", me_res.status_code)
    assert me_res.status_code == 200, f"Get Me failed: {me_res.json()}"
    assert me_res.json()["data"]["email"] == test_email

    print("\n--- Testing Forgot Password ---")
    forgot_res = client.post("/auth/forgot-password", json={"email": test_email})
    print("Forgot Password Status:", forgot_res.status_code)
    assert forgot_res.status_code == 200, f"Forgot password failed: {forgot_res.json()}"

    print("\n--- Testing Logout ---")
    logout_res = client.post("/auth/logout", headers={"Authorization": f"Bearer {new_access_token}"})
    print("Logout Status:", logout_res.status_code)
    assert logout_res.status_code == 200, f"Logout failed: {logout_res.json()}"

    print("\n[SUCCESS] All Authentication tests passed cleanly!")


if __name__ == "__main__":
    test_auth_flow()
