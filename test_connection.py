from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    DATABASE_URL = 'postgresql://payvry_user:7GC6wONvscTxaSmGdUNYxvHt4g4EukzR@dpg-ct7j07pu0jms73ds0dhg-a.oregon-postgres.render.com:5432/payvry'
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables")
        return

    try:
        # Create engine with SSL mode
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30
            }
        )
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    test_connection()
