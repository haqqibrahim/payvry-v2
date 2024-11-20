from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    whatsapp_number: str
    mobile_number: str
    password: str

class UserLogin(BaseModel):
    whatsapp_number: str
    password: str

class OTPVerify(BaseModel):
    whatsapp_number: str
    otp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    whatsapp_number: str
    mobile_number: str
    is_verified: bool
    
    class Config:
        from_attributes = True 