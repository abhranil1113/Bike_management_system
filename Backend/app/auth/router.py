# app/auth/router.py

from typing import Optional
from fastapi import APIRouter, Depends, Request, Header, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User
from app.api.deps import get_current_user
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    StandardResponse,
)
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    forgot_password_service,
    reset_password_service,
    change_password_service,
    logout_user_service,
    logout_all_sessions_service,
    verify_email_token_service,
    build_user_brief,
)

router = APIRouter(tags=["Authentication"])


# Helper to get IP and User-Agent from Request
def get_client_info(request: Request):
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip, user_agent


# ============================================================
# PUBLIC AUTH ENDPOINTS
# ============================================================

@router.post("/register", response_model=StandardResponse, summary="Register new Owner or Driver")
async def register_api(
    req: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip, ua = get_client_info(request)
    result = await register_user(db, req, ip_address=ip, user_agent=ua)
    return StandardResponse(
        success=True,
        message="Registration successful.",
        data=result
    )


@router.post("/login", response_model=StandardResponse, summary="Email + Password Signin")
async def login_api(
    req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip, ua = get_client_info(request)
    result = await login_user(db, req, ip_address=ip, user_agent=ua)
    return StandardResponse(
        success=True,
        message="Login successful.",
        data=result
    )


@router.post("/refresh-token", response_model=StandardResponse, summary="Refresh Access Token with Token Rotation")
async def refresh_token_api(
    req: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip, ua = get_client_info(request)
    result = await refresh_access_token(db, req.refresh_token, ip_address=ip, user_agent=ua)
    return StandardResponse(
        success=True,
        message="Token refreshed successfully.",
        data=result
    )


@router.post("/forgot-password", response_model=StandardResponse, summary="Request Password Reset Link/Token")
async def forgot_password_api(
    req: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    result = await forgot_password_service(db, req.email)
    return StandardResponse(
        success=True,
        message=result["message"],
        data=result
    )


@router.post("/reset-password", response_model=StandardResponse, summary="Reset Password with Token")
async def reset_password_api(
    req: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    result = await reset_password_service(db, req.reset_token, req.new_password)
    return StandardResponse(
        success=True,
        message=result["message"]
    )


@router.get("/verify-email", response_model=StandardResponse, summary="Verify User Email")
async def verify_email_api(
    token: str = Query(..., description="Email verification token"),
    db: Session = Depends(get_db)
):
    result = await verify_email_token_service(db, token)
    return StandardResponse(
        success=True,
        message=result["message"]
    )


# ============================================================
# AUTHENTICATED ENDPOINTS
# ============================================================

@router.get("/me", response_model=StandardResponse, summary="Get Current Authenticated User Profile")
async def get_me_api(
    current_user: User = Depends(get_current_user)
):
    return StandardResponse(
        success=True,
        message="Current user fetched successfully.",
        data=build_user_brief(current_user)
    )


@router.post("/change-password", response_model=StandardResponse, summary="Change Password for Authenticated User")
async def change_password_api(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await change_password_service(db, current_user, req.current_password, req.new_password)
    return StandardResponse(
        success=True,
        message=result["message"]
    )


@router.post("/logout", response_model=StandardResponse, summary="Logout Current Device Session")
async def logout_api(
    authorization: str = Header(..., alias="Authorization"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await logout_user_service(db, current_user, authorization)
    return StandardResponse(
        success=True,
        message=result["message"]
    )


@router.post("/logout-all", response_model=StandardResponse, summary="Logout All Active Sessions/Devices")
async def logout_all_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await logout_all_sessions_service(db, current_user)
    return StandardResponse(
        success=True,
        message=result["message"]
    )