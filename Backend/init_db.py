from database import engine, Base
from Auth.models import User  # Import only the User model

def init_db():
    Base.metadata.drop_all(bind=engine)  # Drop all tables
    Base.metadata.create_all(bind=engine)  # Create all tables

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 