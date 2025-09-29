import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_session
from src.models import User
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

from src.main import app  

client = TestClient(app)

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_register_user_success():
    """Test successful user registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "user"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"
    assert "id" in data
    assert data["wallet_bal"] == 100000.0

def test_register_user_duplicate_username():
    """Test registration with duplicate username"""
    client.post(
        "/auth/register",
        json={
            "username": "duplicateuser",
            "password": "testpass123",
            "role": "user"
        }
    )
    
    response = client.post(
        "/auth/register",
        json={
            "username": "duplicateuser",
            "password": "testpass123",
            "role": "user"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_user_weak_password():
    """Test registration with weak password"""
    response = client.post(
        "/auth/register",
        json={
            "username": "weakpassuser",
            "password": "123",  
            "role": "user"
        }
    )
    assert response.status_code == 422  

def test_login_success():
    """Test successful login"""
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "password": "loginpass123",
            "role": "user"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_wrong_password():
    """Test login with wrong password"""
    client.post(
        "/auth/register",
        json={
            "username": "wrongpassuser",
            "password": "correctpass123",
            "role": "user"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_get_current_user_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_get_current_user_with_valid_token():
    """Test accessing protected endpoint with valid token"""
    client.post(
        "/auth/register",
        json={
            "username": "tokenuser",
            "password": "tokenpass123",
            "role": "user"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "username": "tokenuser",
            "password": "tokenpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tokenuser"
