from dotenv import load_dotenv
import requests
import json
import os
from pathlib import Path
import asyncio
from urllib.parse import urlencode


from Utils.whatsapp_utils import send_whatsapp

load_dotenv()

FLW_SECRET_KEY='FLWSECK-8f7d6404041295af7f5ec678461e252c-1938bfb493bvt-X'
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
FLUTTERWAVE_API_URL = "https://api.flutterwave.com/v3/accounts/resolve"

# Load bank data
BANK_JSON_PATH = Path(__file__).parent.parent / "AI" / "bank.json"
with open(BANK_JSON_PATH, "r") as f:
    BANK_DATA = json.load(f)
    BANKS = BANK_DATA["data"]

def get_bank_code(bank_name: str) -> str:
    """Get bank code from bank name"""
    for bank in BANKS:
        if bank["name"].lower() == bank_name.lower():
            return bank["code"]
    raise ValueError(f"Bank '{bank_name}' not found")

def verify_bank_account(account_number: str, bank: str, whatsapp_number: str, amount: str) -> str:
    print(f'the bank {bank}')
    """Verify a bank account using Flutterwave's API
    
    Args:
        account_number (str): The account number to verify
        bank (str): The bank code (e.g., "033")
        whatsapp_number (str): The user's WhatsApp number
        amount (str): The amount to be transferred

    Returns:
        str: json string containing the status and message
    """
    try:
        bank_code = get_bank_code(bank)
        print(f'the code {bank_code}')

        headers = {
            'Authorization': f'Bearer {FLW_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        print('1')
        params = {
            'account_number': account_number,
            'account_bank': bank_code
        }
        print(2)
        response = requests.post(
            FLUTTERWAVE_API_URL,
            headers=headers,
            json=params
        )
        print(3)
        print(response)
        if response.status_code == 200:
            result = response.json()
            handle_transfer_request(whatsapp_number, amount, account_number, bank_code, bank_name=bank, recipient_name=result['data']['account_name'])
            return json.dumps({
                'status': 'success',
                'message': 'Transfer authorization request sent'
            })
        else:
            return json.dumps({
                'status': 'error',
                'message': 'Failed to verify account'
            })
            
    except ValueError as e:
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })


def handle_transfer_request(whatsapp_number: str, amount: str, account_number: str, bank_code: str, bank_name: str, recipient_name: str):
    print(f"the bank code is {bank_code} made by {whatsapp_number}")
    """
    Args:
        user_id (str): The user's phone number
        amount (str): The amount to be transferred
        account_number (str): The recipient's account number
        bank_code (str): The recipient's bank code
        bank_name (str): The recipient's bank name
        recipient_name (str): The recipient's name
        
    Returns:
        str: A message indicating that the transfer authorization request has been sent
    """
    auth_url = f"{WEBHOOK_URL}authorize-transfer?" + urlencode({
        'amount': amount,
        'account_number': account_number,
        'bank_code': bank_code,
        'bank_name': bank_name,
        'recipient_name': recipient_name
    })
    
    message = (
        f"Please authorize the transfer of NGN {amount} to:\n\n"
        f"Name: {recipient_name}\n"
        f"Account: {account_number}\n"
        f"Bank: {bank_name}\n\n"
        f"Click here to authorize: {auth_url}"
    )
    asyncio.create_task(send_whatsapp(whatsapp_number, message))
    