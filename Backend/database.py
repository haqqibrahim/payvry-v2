from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = 'postgresql://neondb_owner:tpGb6hod5xSu@ep-fancy-bush-a55uacji.us-east-2.aws.neon.tech/neondb?sslmode=require'
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure the database connection with SSL requirements
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30
    },
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 