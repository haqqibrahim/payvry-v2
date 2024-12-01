from sqlalchemy.orm import Session
from database import SessionLocal
from Auth.models import User, Transaction
import json
from datetime import datetime, timedelta

def get_balance(whatsapp_number: str) -> str:
    """Get user's current balance"""
    db = SessionLocal()
    print(f'Get balance aza: {whatsapp_number}')
    try:
        user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        if not user:
            return json.dumps({"error": "User not found"})
        print(user)
        return json.dumps({
            "balance": user.balance,
            "account_number": user.account_number,
            "bank_name": user.bank_name
        })
    finally:
        db.close()

def get_transaction_history(whatsapp_number: str, days: int = 7) -> str:
    """Get user's transaction history for the specified number of days"""
    db = SessionLocal()
    print(f'Get transaction history aza: {whatsapp_number}')
    try:
        user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        if not user:
            return json.dumps({"error": "User not found"})
        
        # Get transactions for the last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.created_at >= start_date
        ).order_by(Transaction.created_at.desc()).all()
        
        transaction_list = [{
            "type": t.transaction_type,
            "amount": t.amount,
            "narration": t.narration,
            "date": t.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "reference": t.reference
        } for t in transactions]
        print(transaction_list)
        
        return json.dumps({
            "transactions": transaction_list,
            "total_transactions": len(transaction_list)
        })
    finally:
        db.close()

def get_user_account_info(whatsapp_number: str) -> dict:
    """Get complete user account information including balance and transaction history"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        if not user:
            return None
            
        # Get recent transactions
        start_date = datetime.utcnow() - timedelta(days=7)
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.created_at >= start_date
        ).order_by(Transaction.created_at.desc()).all()
        
        transaction_list = [{
            "type": t.transaction_type,
            "amount": t.amount,
            "narration": t.narration,
            "date": t.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "reference": t.reference
        } for t in transactions]
        
        return {
            "first_name": user.first_name,
            "balance": user.balance,
            "account_number": user.account_number,
            "bank_name": user.bank_name,
            "transactions": transaction_list
        }
    finally:
        db.close()
