from sqlalchemy.orm import Session
from database import SessionLocal
from Auth.models import User
import json

def authenticate_tool(whatsapp_number: str) -> str:
    print(f'Authenticate tool aza: {whatsapp_number}')
    """Check if a user has an account with us using their WhatsApp number.

    Args:
        whatsapp_number (str): The WhatsApp number to check.

    Returns:
        str: JSON string indicating if user exists and their verification status.
    """
    # Create database session
    db = SessionLocal()
    try:
        # Query the database for the user
        user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
        
        # Prepare response
        result = {
            "exists": bool(user),
            "is_verified": user.is_verified if user else False,
            "full_name": user.full_name if user else None
        }
        print(result)
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({
            "exists": False,
            "error": str(e)
        })
    finally:
        db.close()