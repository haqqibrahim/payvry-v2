from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, ARRAY, Float, BIGINT, func
from database import Base  # Import Base from database.py instead of creating new one
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    whatsapp_number = Column(String, unique=True, nullable=False)
    mobile_number = Column(String, unique=True, nullable=False)
    bvn = Column(String(11), unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    face_encoding = Column(ARRAY(Float), nullable=True)
    account_number = Column(String, unique=True, nullable=True)
    bank_name = Column(String, nullable=True)
    bank_code = Column(String, nullable=True)
    payable_code = Column(String, unique=True, nullable=True)
    balance = Column(Float, default=0.0)

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_number = Column(String, nullable=False)
    otp_code = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # credit or debit
    reference = Column(String, unique=True, nullable=False)
    narration = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 
    
class ChatHistory(Base):
    __tablename__ = "Chat_Memory"  # Use a descriptive table name

    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each message
    user_id = Column(Integer, nullable=False, index=True)  # ID of the user involved in the conversation
    user_message = Column(String, nullable=False)  # Message sent by the user
    agent_response = Column(String, nullable=True)  # Response from the agent (nullable in case of no reply yet)
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of when the message was created

    def __repr__(self):
        return f"<ChatHistory(user_id={self.user_id}, user_message={self.user_message}, agent_response={self.agent_response}, timestamp={self.timestamp})>"