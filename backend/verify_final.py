import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.email_service import email_service

async def test():
    try:
        success = await email_service.send_email(settings.EMAIL_ADDRESS, "Final Test", "It works!")
        if success:
            print("VERIFICATION_SUCCESS")
        else:
            print("VERIFICATION_FAILURE")
    except Exception as e:
        print(f"VERIFICATION_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
