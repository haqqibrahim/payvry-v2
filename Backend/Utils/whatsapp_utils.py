import aiohttp
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

WA_API_URL = os.getenv('WHATSAPP_API_URL')
WA_API_KEY = os.getenv('WHATSAPP_API_KEY')

async def send_whatsapp(
    phone_number: str,
    message: str,
    quoted: Optional[str] = None,
    ephemeral: int = 604800,
    typing_time: int = 0,
    no_link_preview: bool = True,
    mentions: List[str] = None,
    view_once: bool = False
) -> bool:
    """
    Send a WhatsApp message using the API
    
    Args:
        phone_number: Phone number in format "234XXXXXXXXXX"
        message: Message text to send
        quoted: Message ID to quote/reply to
        ephemeral: Message disappearing time in seconds
        typing_time: Typing indicator time in milliseconds
        no_link_preview: Disable link previews
        mentions: List of WhatsApp IDs to mention
        view_once: Whether message can only be viewed once
    """
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WA_API_KEY}"
        }

        payload = {
            "to": f"{phone_number}@s.whatsapp.net",
            "body": message,
            "ephemeral": ephemeral,
            "typing_time": typing_time,
            "no_link_preview": no_link_preview,
            "view_once": view_once
        }

        if quoted:
            payload["quoted"] = quoted
        if mentions:
            payload["mentions"] = [f"{m}@s.whatsapp.net" for m in mentions]

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{WA_API_URL}/messages/text",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return True
                print(f"WhatsApp API error: {await response.text()}")
                return False

    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False 