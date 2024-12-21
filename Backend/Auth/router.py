from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Body, Form
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas
from .security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from Utils.whatsapp_utils import send_whatsapp
from Utils.phone_utils import format_phone_number
from Utils.face_rekognition import Register_Face, Verify_Face
import random
import string
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from Tools.create_account import create_bank_account, BankAccountCreationError
from Tools.bank_verification_tool import verify_bank_account
from Tools.bank_transfer_tool import bank_transfer_tool
import json
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Add OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Helper function to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/signup", response_model=schemas.Token)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Format phone numbers
        formatted_whatsapp = format_phone_number(user.whatsapp_number)
        formatted_mobile = format_phone_number(user.mobile_number)
        
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            (models.User.email == user.email) |
            (models.User.whatsapp_number == formatted_whatsapp) |
            (models.User.mobile_number == formatted_mobile) |
            (models.User.bvn == user.bvn)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email, phone number, or BVN already exists"
            )
        
        # Create new user with formatted numbers
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            whatsapp_number=formatted_whatsapp,
            mobile_number=formatted_mobile,
            bvn=user.bvn,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token for the new user
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )

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
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Return token instead of redirecting
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register-face")
async def register_user_face(
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create temp directory if it doesn't exist
        os.makedirs('temp', exist_ok=True)
        
        # Save uploaded file temporarily
        temp_image_path = f"temp/{image.filename}"
        with open(temp_image_path, "wb") as buffer:
            image_data = await image.read()
            buffer.write(image_data)
        
        # Register face using the temp file path
        result = Register_Face(str(current_user.id), temp_image_path)
        
        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            
        if isinstance(result, str):  # Error message
            raise HTTPException(status_code=400, detail=result)
            
        # Update user verification status
        current_user.is_verified = True
        
        # Create bank account for the verified user
        try:
            account_details = await create_bank_account(
                str(current_user.id),
                current_user.first_name,
                current_user.middle_name,
                current_user.last_name,
                current_user.email,
                current_user.bvn,
                current_user.whatsapp_number
            )
            
            # Update user with bank account details
            current_user.account_number = account_details["account_number"]
            current_user.bank_name = account_details["bank_name"]
            current_user.bank_code = account_details["bank_code"]
            current_user.payable_code = account_details["order_ref"]
            
            # Prepare welcome message with account details
            welcome_message = (
                f"Welcome to Payvry! Your account has been verified successfully.\n\n"
                f"Your bank account details:\n"
                f"Account Number: {account_details['account_number']}\n"
                f"Bank: {account_details['bank_name']}\n"
                f"Account Name: {account_details['account_name']}\n\n"
                f"You can now start interacting with the Payvry AI."
            )
            
        except BankAccountCreationError as e:
            # Log the error but don't stop the verification process
            print(f"Error creating bank account: {str(e)}")
            welcome_message = "Welcome to Payvry! Your account has been verified successfully. However, there was an issue creating your bank account. Please contact support."
        
        db.commit()
        print(current_user.whatsapp_number)
        # Send WhatsApp message
        await send_whatsapp(current_user.whatsapp_number, welcome_message)
        
        return {
            "message": "Face registered successfully and account verified",
            "account_details": account_details if 'account_details' in locals() else None
        }
    
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Add detailed logging
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-face")
async def verify_user_face(
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # if not current_user.face_encoding:
        #     raise HTTPException(status_code=400, detail="No face registered for this user")
        
         # Create temp directory if it doesn't exist
        os.makedirs('temp', exist_ok=True)
        
        # Save uploaded file temporarily
        temp_image_path = f"temp/{image.filename}"
        with open(temp_image_path, "wb") as buffer:
            image_data = await image.read()
            buffer.write(image_data)
        
        # Register face using the temp file path
        result = Verify_Face(str(current_user.id), temp_image_path)
        if result == False:
            raise HTTPException(status_code=400, detail="Face verification failed")
        
        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if isinstance(result, str):  # Error message
                raise HTTPException(status_code=400, detail=result)
                
        return {"message": "Face verified successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/authorize-transfer")
async def authorize_transfer(
    image: UploadFile = File(...),
    transfer_details: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Read image data
        image_data = await image.read()
        # Parse JSON string into a Python dictionary
        transfer_details = json.loads(transfer_details)
        
        # Verify face
        if not current_user.face_encoding:
            raise HTTPException(status_code=400, detail="No face registered for this user")
        
        # Verify face
        is_match = await verify_face(image_data, current_user.face_encoding)
        
        if not is_match:
            raise HTTPException(status_code=401, detail="Face verification failed")
            
        # If face verification successful, proceed with transfer
        result = await bank_transfer_tool(
            whatsapp_number=current_user.whatsapp_number,
            account_bank=transfer_details["account_bank"],
            account_number=transfer_details["account_number"],
            amount=transfer_details["amount"],
            recipient_name=transfer_details["recipient_name"]
        )
        
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  