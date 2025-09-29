import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for testing instead of PostgreSQL
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Remove the test connection function that's causing the error
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        # Don't raise the exception during import
        pass

# Don't call test_db_connection() during import