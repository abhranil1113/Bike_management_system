# app/api/deps.py

from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schema import User, UserLifecycleStatus, UserRole
from app.core.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extracts and verifies JWT token to return authenticated User."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub") or payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active or user.lifecycle_status != UserLifecycleStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is inactive or {user.lifecycle_status.value}",
        )

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """Role-based authorization dependency guard."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        normalized_allowed = [r.lower() for r in allowed_roles]
        if user_role_str.lower() not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {allowed_roles}",
            )
        return current_user
    return role_checker


def get_current_admin(current_user: User = Depends(require_roles(["admin"]))) -> User:
    return current_user


def get_current_owner(current_user: User = Depends(require_roles(["owner"]))) -> User:
    return current_user


def get_current_driver(current_user: User = Depends(require_roles(["driver"]))) -> User:
    return current_user