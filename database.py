import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

# Use SQLite for testing
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
