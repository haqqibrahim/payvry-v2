from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas
from .security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from Utils.whatsapp_utils import send_whatsapp
from Utils.phone_utils import format_phone_number
import random
import string
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from Utils.face_recognition import register_face, verify_face
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

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
        
        # Create access token for the new user
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        # Return token instead of redirecting
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        # Log the error message
        print(f"Error during signup: {str(e)}")  # Log the error
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
        # Read image data
        image_data = await image.read()
        
        # Register face using actual user ID
        face_encoding = await register_face(image_data, str(current_user.id))
        
        # Update user in database with face encoding
        current_user.face_encoding = face_encoding
        db.commit()
        
        return {"message": "Face registered successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-face")
@router.post("/verify-face")
async def verify_user_face(
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.face_encoding:
            raise HTTPException(status_code=400, detail="No face registered for this user")
        
        # Read image data
        image_data = await image.read()
        
        # Verify face
        is_match = await verify_face(image_data, current_user.face_encoding)
        
        if not is_match:
            raise HTTPException(status_code=401, detail="Face verification failed")
        
        return {"message": "Face verified successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user
  