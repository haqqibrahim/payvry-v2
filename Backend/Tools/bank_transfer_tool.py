import os
import aiohttp
import json
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
import uuid
from database import SessionLocal
from Auth.models import User, Transaction

load_dotenv()

FLUTTERWAVE_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLUTTERWAVE_API_URL = "https://api.flutterwave.com/v3/transfers"

async def make_transfer(
    account_bank: str,
    account_number: str,
    amount: float,
    narration: Optional[str] = "Payment from Payvry",
    currency: str = "NGN",
    reference: Optional[str] = None
) -> dict:
    """
    Make a bank transfer using Flutterwave API
    
    Args:
        account_bank (str): Bank code (e.g., "044" for Access Bank)
        account_number (str): Recipient's account number
        amount (float): Amount to transfer
        narration (str, optional): Transfer description. Defaults to "Payment from Payvry"
        currency (str, optional): Currency code. Defaults to "NGN"
        reference (str, optional): Unique transfer reference. Generated if not provided
    
    Returns:
        dict: API response containing transfer details
    """
    try:
        # Generate unique reference if not provided
        if not reference:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            reference = f"PVY_{timestamp}_{str(uuid.uuid4())[:8]}"

        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "account_bank": account_bank,
            "account_number": account_number,
            "amount": amount,
            "narration": narration,
            "currency": currency,
            "reference": reference
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                FLUTTERWAVE_API_URL,
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise Exception(f"Transfer failed: {result.get('message', 'Unknown error')}")
                
                return result

    except Exception as e:
        print(f"Error making transfer: {str(e)}")
        raise Exception(f"Failed to process transfer: {str(e)}")

async def bank_transfer_tool(
    whatsapp_number: str,
    account_bank: str,
    account_number: str,
    amount: float,
    recipient_name: str
) -> str:
    """
    Make a bank transfer to another account
    
    Args:
        whatsapp_number (str): Sender's WhatsApp number
        account_bank (str): Recipient's bank code
        account_number (str): Recipient's account number
        amount (float): Amount to transfer
        recipient_name (str): Name of the recipient
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        
        if not user:
            return json.dumps({"error": "User not found"})
            
        if user.balance < amount:
            return json.dumps({"error": f"Insufficient balance. Your current balance is NGN {user.balance:,.2f}"})
        
        # Generate reference
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        reference = f"PVY_{timestamp}_{str(uuid.uuid4())[:8]}"
        
        # Create transaction record (pending)
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type="debit",
            reference=reference,
            narration=f"Transfer to {recipient_name}",
            status="pending"
        )
        db.add(transaction)
        
        # Deduct from user's balance
        user.balance -= amount
        db.commit()
        
        # Make the transfer
        transfer_result = await make_transfer(
            account_bank=account_bank,
            account_number=account_number,
            amount=amount,
            narration=f"Transfer from {user.first_name}",
            reference=reference
        )
        
        if transfer_result['status'] == 'success':
            # Update transaction status based on transfer response
            transaction.status = 'processing'
            transaction.reference = transfer_result['data']['reference']
            db.commit()
            
            return json.dumps({
                "status": "success",
                "message": f"Transfer of NGN {amount:,.2f} to {recipient_name} is being processed",
                "reference": reference,
                "new_balance": user.balance
            })
        else:
            # Rollback the transaction if transfer failed
            transaction.status = "failed"
            user.balance += amount  # Refund the amount
            db.commit()
            
            return json.dumps({
                "error": f"Transfer failed: {transfer_result.get('message', 'Unknown error')}"
            })
            
    except Exception as e:
        if 'transaction' in locals() and 'db' in locals():
            transaction.status = "failed"
            user.balance += amount  # Refund the amount
            db.commit()
        return json.dumps({
            "error": f"Transfer failed: {str(e)}"
        })
    finally:
        if 'db' in locals():
            db.close()
