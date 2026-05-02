#app/auth/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth_schema import (
    SendOTPRequest,
    VerifyOTPRequest,
    SetPasswordRequest,
    LoginRequest
)

from app.services.auth_service import (
    send_otp,
    verify_signup_otp,
    create_user,
    login_user
)

from app.db.database import get_db


# ========================
# ROUTER (NO PREFIX HERE)
# ========================
router = APIRouter(
    tags=["Authentication"]
)


# ========================
# SEND OTP
# ========================
@router.post("/send-otp")
async def send_otp_api(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    result = await send_otp(db, request.email)

    return {
        "success": True,
        "message": "OTP sent successfully",
        "data": result
    }


# ========================
# VERIFY OTP
# ========================
@router.post("/verify-otp")
async def verify_otp_api(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    result = await verify_signup_otp(
        db,
        request.email,
        request.otp
    )

    return {
        "success": True,
        "message": "OTP verified successfully",
        "data": result
    }


# ========================
# SET PASSWORD (SIGNUP)
# ========================
@router.post("/set-password")
async def set_password_api(
    request: SetPasswordRequest,
    db: Session = Depends(get_db)
):
    result = await create_user(
        db,
        request.email,
        request.password,
        request.role
    )

    return {
        "success": True,
        "message": "User created successfully",
        "data": result
    }


# ========================
# LOGIN
# ========================
@router.post("/login")
async def login_api(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    result = await login_user(
        db,
        request.email,
        request.password
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": result
    }