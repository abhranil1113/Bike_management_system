# app/services/auth_service.py

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.db.schema import (
    User,
    UserRole,
    UserLifecycleStatus,
    UserSession,
    OwnerProfile,
    DriverProfile,
    Wallet,
    EmailVerificationToken,
    PasswordResetToken,
    AdminAuditLog,
    AuditActorType,
    utcnow,
)
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.core.email import send_otp_email


def hash_token(token: str) -> str:
    """Helper to produce SHA256 hash of tokens for DB storage."""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def get_user_full_name(user: User) -> str:
    """Helper to extract user full name from owner or driver profile."""
    if user.owner_profile and user.owner_profile.full_name:
        return user.owner_profile.full_name
    if user.driver_profile and user.driver_profile.full_name:
        return user.driver_profile.full_name
    return user.email.split("@")[0]


def build_user_brief(user: User) -> Dict[str, Any]:
    """Builds user profile dictionary for API responses."""
    return {
        "id": user.id,
        "full_name": get_user_full_name(user),
        "email": user.email,
        "phone": user.phone,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_verified": user.is_verified,
        "is_active": user.is_active,
    }


# ============================================================
# REGISTER USER
# ============================================================
async def register_user(
    db: Session,
    request: RegisterRequest,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    # 1. Check existing email & phone
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email address already exists.",
        )

    if db.query(User).filter(User.phone == request.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists.",
        )

    # 2. Validate password strength
    strength_errors = validate_password_strength(request.password)
    if strength_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weak password: {'; '.join(strength_errors)}",
        )

    # 3. Hash password securely with bcrypt
    hashed_pwd = hash_password(request.password)

    # 4. Map role enum
    role_enum = UserRole(request.role.lower())

    # 5. Create user entity
    user = User(
        email=request.email.lower(),
        phone=request.phone.strip(),
        role=role_enum,
        hashed_password=hashed_pwd,
        is_active=True,
        is_verified=not settings.REQUIRE_EMAIL_VERIFICATION,
        lifecycle_status=UserLifecycleStatus.ACTIVE,
    )
    db.add(user)
    db.flush()

    # 6. Create corresponding profile based on role
    if role_enum == UserRole.OWNER:
        owner_prof = OwnerProfile(
            user_id=user.id,
            full_name=request.full_name.strip(),
            phone=request.phone.strip(),
        )
        db.add(owner_prof)
    elif role_enum == UserRole.DRIVER:
        driver_prof = DriverProfile(
            user_id=user.id,
            full_name=request.full_name.strip(),
        )
        db.add(driver_prof)

    # 7. Create wallet for user
    wallet = Wallet(user_id=user.id, balance=0.00)
    db.add(wallet)

    # 8. Create tokens & session
    token_payload = {"sub": user.id, "email": user.email, "role": role_enum.value}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    session_entry = UserSession(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        is_active=True,
    )
    db.add(session_entry)

    # 9. Audit log
    audit_log = AdminAuditLog(
        actor_user_id=user.id,
        actor_type=AuditActorType.SYSTEM,
        action="USER_REGISTER",
        entity_type="users",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)

    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": build_user_brief(user),
    }


# ============================================================
# LOGIN USER
# ============================================================
async def login_user(
    db: Session,
    request: LoginRequest,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    user = db.query(User).filter(User.email == request.email.lower()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check account lock status
    if user.locked_until and user.locked_until > utcnow():
        lock_remaining = int((user.locked_until - utcnow()).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to multiple failed login attempts. Try again in {lock_remaining} minutes.",
        )

    # Verify password using bcrypt
    if not verify_password(request.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.locked_until = utcnow() + timedelta(minutes=settings.LOCKOUT_MINUTES)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Reset failed login counters on success
    user.failed_login_attempts = 0
    user.locked_until = None

    # Check status
    if not user.is_active or user.lifecycle_status != UserLifecycleStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is inactive or {user.lifecycle_status.value}",
        )

    # Generate Access & Refresh tokens
    token_payload = {"sub": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    session_entry = UserSession(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        is_active=True,
    )
    db.add(session_entry)

    # Audit log
    audit_log = AdminAuditLog(
        actor_user_id=user.id,
        actor_type=AuditActorType.SYSTEM,
        action="USER_LOGIN",
        entity_type="users",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)

    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": build_user_brief(user),
    }


# ============================================================
# REFRESH TOKEN (TOKEN ROTATION)
# ============================================================
async def refresh_access_token(
    db: Session,
    refresh_token_str: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    payload = decode_refresh_token(refresh_token_str)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    r_hash = hash_token(refresh_token_str)

    session_entry = (
        db.query(UserSession)
        .filter(UserSession.refresh_token_hash == r_hash, UserSession.is_active == True)
        .first()
    )

    if not session_entry or session_entry.expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalidated",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Invalidate old session (Rotation)
    session_entry.is_active = False

    # Create new tokens & session
    token_payload = {"sub": user.id, "email": user.email, "role": user.role.value}
    new_access_token = create_access_token(token_payload)
    new_refresh_token = create_refresh_token(token_payload)

    new_session = UserSession(
        user_id=user.id,
        token_hash=hash_token(new_access_token),
        refresh_token_hash=hash_token(new_refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        is_active=True,
    )
    db.add(new_session)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": build_user_brief(user),
    }


# ============================================================
# FORGOT & RESET PASSWORD
# ============================================================
async def forgot_password_service(db: Session, email: str) -> Dict[str, Any]:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        # Avoid email enumeration security leak
        return {"message": "If an account exists with this email, a reset token has been generated."}

    token_str = hashlib.sha256(f"{user.id}:{datetime.now().timestamp()}".encode()).hexdigest()
    expires_at = utcnow() + timedelta(minutes=15)

    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=token_str,
        expires_at=expires_at,
    )
    db.add(reset_entry)
    db.commit()

    # In production, send via email. Return in response data for easy testing/dev.
    return {
        "message": "Password reset token created successfully.",
        "reset_token": token_str,
    }


async def reset_password_service(
    db: Session, reset_token_str: str, new_password: str
) -> Dict[str, Any]:
    reset_entry = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == reset_token_str,
            PasswordResetToken.used_at == None,
        )
        .first()
    )

    if not reset_entry or reset_entry.expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    strength_errors = validate_password_strength(new_password)
    if strength_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weak password: {'; '.join(strength_errors)}",
        )

    user = db.query(User).filter(User.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    reset_entry.used_at = utcnow()

    # Revoke all existing JWT sessions for security
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})
    db.commit()

    return {"message": "Password has been reset successfully. Please log in with your new password."}


# ============================================================
# CHANGE PASSWORD
# ============================================================
async def change_password_service(
    db: Session, user: User, current_password: str, new_password: str
) -> Dict[str, Any]:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    strength_errors = validate_password_strength(new_password)
    if strength_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weak password: {'; '.join(strength_errors)}",
        )

    user.hashed_password = hash_password(new_password)
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})
    db.commit()

    return {"message": "Password updated successfully. All active sessions invalidated."}


# ============================================================
# LOGOUT / LOGOUT ALL
# ============================================================
async def logout_user_service(db: Session, user: User, auth_header: str) -> Dict[str, Any]:
    token_str = auth_header.replace("Bearer ", "").strip()
    t_hash = hash_token(token_str)
    db.query(UserSession).filter(UserSession.token_hash == t_hash).update({"is_active": False})
    db.commit()
    return {"message": "Logged out successfully."}


async def logout_all_sessions_service(db: Session, user: User) -> Dict[str, Any]:
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})
    db.commit()
    return {"message": "Logged out from all devices successfully."}


# ============================================================
# VERIFY EMAIL
# ============================================================
async def verify_email_token_service(db: Session, token_str: str) -> Dict[str, Any]:
    token_entry = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token == token_str,
            EmailVerificationToken.used_at == None,
        )
        .first()
    )

    if not token_entry or token_entry.expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user = db.query(User).filter(User.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    token_entry.used_at = utcnow()
    db.commit()

    return {"message": "Email verified successfully. You may now log in."}