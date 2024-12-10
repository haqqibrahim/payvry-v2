# This function is used to create a new bank account for the user

from typing import Dict
import os
from fastapi import HTTPException
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class BankAccountCreationError(Exception):
    pass
    
async def create_bank_account(user_id: str, first_name: str, middle_name: str, last_name: str, email: str, bvn: str, phone: str) -> Dict:
    """
    Create a virtual bank account for a user using Paystack API.
    
    Args:
        user_id (str): User's ID
        first_name (str): User's first name
        middle_name (str): User's middle name
        last_name (str): User's last name
        email (str): User's email
        bvn (str): User's BVN
        phone (str): User's phone number
        
    Returns:
        dict: Account details including account number, bank name, etc.
        
    Raises:
        BankAccountCreationError: If account creation fails
    """
    try:
        # Get token from environment variable
        token = os.getenv("FLW_SECRET_KEY")
        
        if not token:
            raise BankAccountCreationError("Missing Flutterwave credentials")

        # Create dedicated account
        result = await create_flw_virtual_account(
            secret_key=token,
            email=email,
            bvn=bvn,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
        )
        
        if result['status'] == 'success':
            account_number = result['data']['account_number']
            account_name = result['data']['note']  # Assuming the note contains the account name
            bank_name = result['data']['bank_name']
            order_ref = result['data']['order_ref']

            print(f"Account Number: {account_number}")
            print(f"Account Name: {account_name}")
            print(f"Bank Name: {bank_name}")
            print(f"Order Reference: {order_ref}")
        else:
            print("Failed to create virtual account:", result['message'])
        
        account_details = {
            "account_number": account_number,
            "account_name": account_name,
            "bank_name": bank_name,
            "bank_code": '123',
            "order_ref": order_ref
        }
        
        # Validate response
        if not all(account_details.values()):
            raise BankAccountCreationError("Invalid response from Flutterwave")
            
        return account_details
        
    except Exception as e:
        raise BankAccountCreationError(f"Failed to create bank account: {str(e)}")

async def create_flw_virtual_account(secret_key: str, email: str, bvn: str, first_name: str, middle_name: str, last_name: str) -> dict:
    """
    Create a virtual account using Flutterwave's API.
    
    Args:
        secret_key (str): Flutterwave secret key
        email (str): Customer's email address
        
    Returns:
        dict: Response from Flutterwave API containing virtual account details
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    url = 'https://api.flutterwave.com/v3/virtual-account-numbers'
    key='FLWSECK-8f7d6404041295af7f5ec678461e252c-1938bfb493bvt-X'
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'email': email,
        'bvn': bvn,
        "is_permanent": True,
        "first_name": first_name,
        "last_name": last_name,
        "narration": f"{first_name} {middle_name} {last_name}"
        
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
    
    return response.json()
