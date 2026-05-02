from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV
# =========================
load_dotenv()

EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")

# =========================
# VALIDATION (IMPORTANT FIX)
# =========================
if not EMAIL_USERNAME or not EMAIL_PASSWORD or not EMAIL_FROM:
    raise ValueError("❌ Email credentials missing in .env file")

# =========================
# DEBUG (TEMP ONLY - REMOVE IN PROD)
# =========================
print("EMAIL CONFIG LOADED ✔")
print("USERNAME:", EMAIL_USERNAME)
print("FROM:", EMAIL_FROM)

# =========================
# CONFIG
# =========================
conf = ConnectionConfig(
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD,
    MAIL_FROM=EMAIL_FROM,
    MAIL_PORT=EMAIL_PORT,
    MAIL_SERVER=EMAIL_HOST,

    # Gmail requires STARTTLS
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False  # ⚠️ FIX: prevents SSL issues in dev systems
)

fm = FastMail(conf)


# =========================
# SEND OTP EMAIL
# =========================
async def send_otp_email(email: str, otp: str):
    try:
        message = MessageSchema(
            subject="Your OTP Code - Bike Management System",
            recipients=[email],
            body=f"""
Hello,

Your OTP for verification is: {otp}

This OTP is valid for 5 minutes.
Do not share it with anyone.

Regards,
Bike Management System
            """,
            subtype="plain"
        )

        await fm.send_message(message)

        print(f"✅ OTP email sent successfully to {email}")

    except Exception as e:
        print("❌ EMAIL SENDING FAILED:", str(e))
        raise e