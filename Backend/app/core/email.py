from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")


async def send_otp_email(email: str, otp: str):
    try:
        if not EMAIL_USERNAME or not EMAIL_PASSWORD:
            print(f"[EMAIL MOCK] Sending OTP {otp} to {email}")
            return
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
        conf = ConnectionConfig(
            MAIL_USERNAME=EMAIL_USERNAME,
            MAIL_PASSWORD=EMAIL_PASSWORD,
            MAIL_FROM=EMAIL_FROM,
            MAIL_PORT=EMAIL_PORT,
            MAIL_SERVER=EMAIL_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False
        )
        fm = FastMail(conf)
        message = MessageSchema(
            subject="Your Verification Code - Bike Management System",
            recipients=[email],
            body=f"Hello,\n\nYour code is: {otp}\n\nRegards,\nBike Management System",
            subtype="plain"
        )
        await fm.send_message(message)
        print(f"[EMAIL] Verification email sent to {email}")
    except Exception as e:
        print("[EMAIL FAILED]", str(e))