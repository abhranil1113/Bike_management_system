# app/schemas/auth_schema.py

from typing import Optional, Literal, Any
from pydantic import BaseModel, EmailStr, Field, model_validator


# ========================
# SIGNUP / REGISTER
# ========================
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, example="John Doe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    phone: str = Field(..., min_length=10, max_length=15, example="9876543210")
    password: str = Field(..., min_length=6, example="Secret123!")
    confirm_password: str = Field(..., min_length=6, example="Secret123!")
    role: Literal["owner", "driver", "admin"] = Field(..., example="driver")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# ========================
# LOGIN
# ========================
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., example="Secret123!")


# ========================
# REFRESH TOKEN
# ========================
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT Refresh Token")


# ========================
# FORGOT & RESET PASSWORD
# ========================
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="johndoe@example.com")


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(..., description="Password reset token sent to email")
    new_password: str = Field(..., min_length=6, example="NewSecret123!")
    confirm_password: str = Field(..., min_length=6, example="NewSecret123!")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# ========================
# CHANGE PASSWORD
# ========================
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., example="OldSecret123!")
    new_password: str = Field(..., min_length=6, example="NewSecret123!")
    confirm_password: str = Field(..., min_length=6, example="NewSecret123!")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# ========================
# RESPONSE SCHEMAS
# ========================
class UserBrief(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    role: str
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True


class AuthTokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief


class StandardResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None