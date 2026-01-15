import os
import aiosmtplib
from email.message import EmailMessage
from typing import List
from config import settings

class EmailService:
    async def send_email(self, to_email: str, subject: str, body: str):
        if not settings.EMAIL_ADDRESS or not settings.EMAIL_PASSWORD:
            print("WARNING: Email credentials not set in settings. Skipping email send.")
            return False
            
        # Clean password (remove spaces often included in App Passwords)
        clean_password = settings.EMAIL_PASSWORD.replace(" ", "")

        message = EmailMessage()
        message["From"] = settings.EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_SERVER,
                port=587, # settings.SMTP_PORT typically 587
                start_tls=True,
                username=settings.EMAIL_ADDRESS,
                password=clean_password,
            )
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"CRITICAL ERROR sending email to {to_email}: {e}")
            try:
                with open("email_error.log", "w") as f:
                    f.write(str(e))
            except:
                pass
            return False

email_service = EmailService()
