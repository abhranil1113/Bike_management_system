#app/api/auth/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth_schema import *
from app.services.auth_service import *
from app.db.session import get_db
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-otp")
def send_otp_api(req: SendOTPRequest, db: Session = Depends(get_db)):
    send_otp(db, req.email)
    return {"message": "OTP sent"}


@router.post("/verify-otp")
def verify_otp_api(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    if not verify_signup_otp(db, req.email, req.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    return {"message": "OTP verified"}


@router.post("/set-password")
def set_password_api(req: SetPasswordRequest, db: Session = Depends(get_db)):
    user = create_user(db, req.email, req.password)
    return {"message": "User created", "user_id": user.id}


@router.post("/login")
def login_api(req: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(db, req.email, req.password)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id})

    return {"access_token": token}