from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)

async def send_otp_email(email: str, otp: str):
    try:
        message = MessageSchema(
            subject="Your OTP Verification Code",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>OTP Verification</h2>
                    <p>Your OTP for verification is: <strong>{otp}</strong></p>
                    <p>This OTP is valid for 10 minutes.</p>
                    <p>If you didn't request this OTP, please ignore this email.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 

async def send_reset_password_email(email: str, reset_token: str):
    subject = "Password Reset Request"
    # You can customize this URL based on your frontend
    reset_url = f"https://your-frontend-url/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You have requested to reset your password. Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
        </body>
    </html>
    """
    
    await send_email(
        email_to=email,
        subject=subject,
        html_content=html_content
    )