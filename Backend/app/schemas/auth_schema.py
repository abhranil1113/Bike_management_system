# app/schemas/auth_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# ========================
# OTP
# ========================
class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


# ========================
# SIGNUP (ADD ROLE HERE)
# ========================
class SetPasswordRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["DRIVER", "OWNER"]   


# ========================
# LOGIN
# ========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ========================
# OPTIONAL RESPONSE MODEL
# ========================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str