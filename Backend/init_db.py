from database import engine, Base
from Auth.models import User, OTP  # Import your models

def init_db():
    Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)  # Create new tables

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 