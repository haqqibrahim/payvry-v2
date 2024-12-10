from sqlalchemy import text
from database import engine, Base
from Auth.models import User, OTP  # Import your models

def init_db():
    # Drop all tables with CASCADE
    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
    
    # Recreate the tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
