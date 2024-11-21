from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas
from .security import get_password_hash, verify_password, create_access_token
from Utils.whatsapp_utils import send_whatsapp
from Utils.phone_utils import format_phone_number
import random
import string
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Format phone numbers
    formatted_whatsapp = format_phone_number(user.whatsapp_number)
    formatted_mobile = format_phone_number(user.mobile_number)
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) |
        (models.User.whatsapp_number == formatted_whatsapp) |
        (models.User.mobile_number == formatted_mobile)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone number already exists"
        )
    
    # Create new user with formatted numbers
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        whatsapp_number=formatted_whatsapp,
        mobile_number=formatted_mobile,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Commenting out the OTP generation and sending logic
    '''
    # Generate and send OTP
    otp = generate_otp()
    db_otp = models.OTP(
        whatsapp_number=formatted_whatsapp,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(db_otp)
    db.commit()
    
    # Send OTP via WhatsApp
    await send_whatsapp(formatted_whatsapp, message=otp)
    '''
    
    return db_user

# Commenting out the verify-otp endpoint
'''
@router.post("/verify-otp")
async def verify_otp(otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    # Format the phone number first
    formatted_whatsapp = format_phone_number(otp_data.whatsapp_number)
    
    db_otp = db.query(models.OTP).filter(
        models.OTP.whatsapp_number == formatted_whatsapp,
        models.OTP.otp_code == otp_data.otp_code,
        models.OTP.is_verified == False
    ).first()
    
    if not db_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Mark OTP as verified
    db_otp.is_verified = True
    
    # Mark user as verified
    user = db.query(models.User).filter(
        models.User.whatsapp_number == formatted_whatsapp
    ).first()
    user.is_verified = True
    
    db.commit()
    
    return {"message": "OTP verified successfully"}
'''

@router.post("/login", response_model=schemas.Token)
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Format the phone number first
    formatted_whatsapp = format_phone_number(user_credentials.whatsapp_number)
    
    user = db.query(models.User).filter(
        models.User.whatsapp_number == formatted_whatsapp
    ).first()
    
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect whatsapp number or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"} 