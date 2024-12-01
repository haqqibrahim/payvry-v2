from fastapi import APIRouter, Request, Depends, HTTPException
import json
import asyncio
import os
from sqlalchemy.orm import Session

from AI.agent import get_payvry_agent
from Auth.models import User
from database import get_db
from Auth.models import Transaction
from Tools.account_tool import get_user_account_info
from Utils.whatsapp_utils import send_whatsapp

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Change the prefix to match the incoming webhook requests
router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

@router.post("/whatsapp/statuses")
def whatsapp_status_webhook(request: Request):
    return {"status": "success", "message": "Webhook received"}

@router.post("/whatsapp/messages")
async def whatsapp_webhook(request: Request):
    # Get the raw body content
    body = await request.body()
    
    try:
        body_dict = json.loads(body)
        text = body_dict["messages"][0]["text"]["body"]
        user_id = body_dict["messages"][0]["from"]
        print("User ID:", user_id)
        print("Message:", text)
        
        # Get user account information
        user_info = get_user_account_info(user_id)
        
        if not user_info:
            # User doesn't have an account
            message = (
                "Welcome to Payvry! 👋\n\n"
                "To interact with our AI assistant, you'll need to create an account first. "
                "Please click the link below to sign up:\n\n"
                f"{WEBHOOK_URL}signup"
            )
            await send_whatsapp(phone_number=user_id, message=message)
            return {"status": "success", "message": "Signup message sent"}
        
        # User has an account, create agent with user context
        agent_context = (
            f"User Information:\n"
            f"Name: {user_info['first_name']}\n"
            f"Current Balance: NGN {user_info['balance']:,.2f}\n"
            f"Account Number: {user_info['account_number']}\n"
            f"Bank: {user_info['bank_name']}\n\n"
            f"Recent Transactions: {len(user_info['transactions'])} in the last 7 days"
        )
        
        # Create background task with user context
        asyncio.create_task(
            get_payvry_agent(
                user_id=user_id,
                message=text,
                user_context=agent_context
            )
        )

        return {"status": "success", "message": "Webhook received"}
        
    except json.JSONDecodeError as e:
        print("Failed to parse webhook body:", body)
        return {"status": "error", "message": "Invalid JSON payload"}

@router.post("/flutterwave/webhook")
async def handle_flutterwave_webhook(request: Request, db: Session = Depends(get_db)):
    # Get the signature from headers
    flw_signature = request.headers.get("verif-hash")
    
    # Verify webhook signature
    if not flw_signature or flw_signature != os.getenv("FLW_WEBHOOK_HASH"):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Get the webhook payload
    try:
        payload = await request.json()
        print(payload)
        
        # Verify it's a successful charge
        if payload["event"] == "charge.completed" and payload["data"]["status"] == "successful":
            # Get transaction details
            amount = float(payload["data"]["amount"])
            reference = payload["data"]["flw_ref"]
            narration = payload["data"]["narration"]  # This is the sender's name
            customer_email = payload["data"]["customer"]["email"]
            
            # Find user by email
            user = db.query(User).filter(User.email == customer_email).first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Create transaction record
            transaction = Transaction(
                user_id=user.id,
                amount=amount,
                transaction_type="credit",
                reference=reference,
                narration=f"Transfer from {narration}",  # Using sender name from narration
                status="successful"
            )
            
            # Update user balance
            user.balance += amount
            
            # Save changes
            db.add(transaction)
            db.commit()
            
            # Send notification to user
            notification_message = (
                f"Credit Alert! 💰\n\n"
                f"Amount: NGN {amount:,.2f}\n"
                f"From: {narration}\n"
                f"Type: Bank Transfer\n"
                f"Current Balance: NGN {user.balance:,.2f}"
            )
            
            await send_whatsapp(user.whatsapp_number, notification_message)
            
            return {"status": "success", "message": "Webhook processed successfully"}
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 