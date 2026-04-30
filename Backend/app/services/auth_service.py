import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.schema import User, OTPRequest, OTPPurpose
from app.core.security import hash_otp, verify_otp, hash_password, verify_password
from app.core.config import settings


def generate_otp():
    return str(random.randint(100000, 999999))


# STEP 1: Send OTP
def send_otp(db: Session, email: str):
    otp = generate_otp()

    otp_entry = OTPRequest(
        phone=email,  # reuse field (your schema uses phone but we use email)
        otp_code_hash=hash_otp(otp),
        purpose=OTPPurpose.SIGNUP,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    )

    db.add(otp_entry)
    db.commit()

    print("OTP:", otp)  # later replace with email service


# STEP 2: Verify OTP
def verify_signup_otp(db: Session, email: str, otp: str):
    otp_entry = (
        db.query(OTPRequest)
        .filter(OTPRequest.phone == email)
        .order_by(OTPRequest.created_at.desc())
        .first()
    )

    if not otp_entry:
        return False

    if otp_entry.expires_at < datetime.utcnow():
        return False

    if otp_entry.used_at:
        return False

    if not verify_otp(otp, otp_entry.otp_code_hash):
        return False

    otp_entry.used_at = datetime.utcnow()
    db.commit()

    return True


# STEP 3: Set Password & Create User
def create_user(db: Session, email: str, password: str):
    user = User(
        email=email,
        phone=email,  # temporary reuse
        role="driver",  # default role
        is_active=True,
    )

    user.hashed_password = hash_password(password)  # IMPORTANT: Add column later

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# STEP 4: Login
def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user