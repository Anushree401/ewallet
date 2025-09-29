import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import engine, init_db
from sqlmodel import SQLModel

@pytest.fixture(autouse=True)
def setup_database():
    # Create all tables before each test session
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    # Clean up after tests if needed

@pytest.fixture
def client():
    return TestClient(app)
