from pydantic import BaseModel, EmailStr, constr, validator
from typing import Dict

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    whatsapp_number: str
    mobile_number: str
    bvn: constr(min_length=11, max_length=11)
    password: str
    email: EmailStr

    @validator('bvn')
    def validate_bvn(cls, v):
        if not v.isdigit():
            raise ValueError('BVN must contain only digits')
        if len(v) != 11:
            raise ValueError('BVN must be exactly 11 digits')
        return v

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
    first_name: str
    last_name: str
    middle_name: str
    email: str
    whatsapp_number: str
    mobile_number: str
    bvn: str
    is_verified: bool
    
    class Config:
        from_attributes = True 

class CreateAccountRequest(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    phone: str
    preferred_bank: str
    country: str
    account_number: str
    bvn: constr(min_length=11, max_length=11)
    bank_code: str

class BankAccountResponse(BaseModel):
    event: str
    data: Dict[str, Dict]  # You can further define this if you want to be more specific