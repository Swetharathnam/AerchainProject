import os
import aiosmtplib
from email.message import EmailMessage
from typing import List

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

class EmailService:
    async def send_email(self, to_email: str, subject: str, body: str):
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            print("WARNING: Email credentials not set. Skipping email send.")
            return False

        message = EmailMessage()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=SMTP_SERVER,
                port=SMTP_PORT,
                start_tls=True,
                username=EMAIL_ADDRESS,
                password=EMAIL_PASSWORD,
            )
            return True
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False

email_service = EmailService()
