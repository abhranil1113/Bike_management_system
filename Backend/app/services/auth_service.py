import random
import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.schema import (
    OTPRequest,
    OTPPurpose,
    User,
    UserRole
)
from app.core.email import send_otp_email

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# =========================
# OTP GENERATION
# =========================
def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


# =========================
# SEND OTP (SIGNUP)
# =========================
async def send_otp(db: Session, email: str):
    otp = generate_otp()
    otp_hash = hash_otp(otp)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # delete old OTPs
    db.query(OTPRequest).filter(OTPRequest.email == email).delete()

    otp_entry = OTPRequest(
        email=email,
        otp_code_hash=otp_hash,
        purpose=OTPPurpose.SIGNUP,
        expires_at=expires_at
    )

    db.add(otp_entry)
    db.commit()

    await send_otp_email(email, otp)

    return {"email": email, "otp_sent": True}


# =========================
# VERIFY OTP
# =========================
async def verify_signup_otp(db: Session, email: str, otp: str):
    otp_hash = hash_otp(otp)

    otp_entry = (
        db.query(OTPRequest)
        .filter(OTPRequest.phone == email)
        .order_by(OTPRequest.created_at.desc())
        .first()
    )

    if not otp_entry:
        return {"error": "OTP not found"}

    if otp_entry.used_at:
        return {"error": "OTP already used"}

    if otp_entry.expires_at < datetime.now(timezone.utc):
        return {"error": "OTP expired"}

    if otp_entry.otp_code_hash != otp_hash:
        return {"error": "Invalid OTP"}

    otp_entry.used_at = datetime.now(timezone.utc)
    db.commit()

    return {"success": True, "message": "OTP verified"}


# =========================
# CREATE USER (SIGNUP FINAL STEP)
# =========================
async def create_user(db: Session, email: str, password: str, role: str = "driver"):
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        return {"error": "User already exists"}

    hashed_password = hash_password(password)

    user = User(
        email=email,
        phone=email,   # temporary mapping (your schema uses phone required)
        role=UserRole(role)
    )

    # ⚠️ IMPORTANT: password field must exist in schema
    user.password = hashed_password

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================
# LOGIN USER
# =========================
async def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user