import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_auth_headers(username, password):
    """Helper function to get authentication headers"""
    # Register if not exists
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "role": "user"
        }
    )
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_wallet_balance():
    """Test getting wallet balance"""
    headers = get_auth_headers("balanceuser", "balancepass123")
    
    response = client.get("/wallet/balance", headers=headers)
    assert response.status_code == 200
    assert response.json() == 100000.0  # Default balance

def test_top_up_wallet_success():
    """Test successful wallet top-up"""
    headers = get_auth_headers("topupuser", "topuppass123")
    
    response = client.post(
        "/wallet/top-up",
        headers=headers,
        json={"amount": 500.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_bal"] == 100500.0  # Initial 100000 + 500

def test_top_up_wallet_invalid_amount():
    """Test wallet top-up with invalid amount"""
    headers = get_auth_headers("invalidtopup", "invalidpass123")
    
    response = client.post(
        "/wallet/top-up",
        headers=headers,
        json={"amount": -100.0}  # Negative amount
    )
    assert response.status_code == 422  # Validation error

def test_spend_money_success():
    """Test successful spending"""
    headers = get_auth_headers("spenduser", "spendpass123")
    
    response = client.post(
        "/wallet/spend",
        headers=headers,
        json={"amount": 300.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_bal"] == 99700.0  # Initial 100000 - 300

def test_spend_money_insufficient_funds():
    """Test spending with insufficient funds"""
    headers = get_auth_headers("pooruser", "poorpass123")
    
    response = client.post(
        "/wallet/spend",
        headers=headers,
        json={"amount": 200000.0}  # More than initial balance
    )
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]

def test_spend_money_invalid_amount():
    """Test spending with invalid amount"""
    headers = get_auth_headers("invalidspend", "invalidpass123")
    
    response = client.post(
        "/wallet/spend",
        headers=headers,
        json={"amount": 0}  # Zero amount
    )
    assert response.status_code == 422  # Validation error

def test_transfer_money_success():
    """Test successful money transfer"""
    # Create sender
    sender_headers = get_auth_headers("senderuser", "senderpass123")
    
    # Create recipient
    client.post(
        "/auth/register",
        json={
            "username": "recipientuser",
            "password": "recipientpass123",
            "role": "user"
        }
    )
    
    # Transfer money
    response = client.post(
        "/wallet/transfer",
        headers=sender_headers,
        json={
            "recipient_username": "recipientuser",
            "amount": 1000.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Transfer successful"
    assert data["sender_balance"] == 99000.0  # 100000 - 1000

def test_transfer_money_insufficient_funds():
    """Test transfer with insufficient funds"""
    sender_headers = get_auth_headers("poorsender", "poorpass123")
    
    client.post(
        "/auth/register",
        json={
            "username": "richrecipient",
            "password": "richpass123",
            "role": "user"
        }
    )
    
    response = client.post(
        "/wallet/transfer",
        headers=sender_headers,
        json={
            "recipient_username": "richrecipient",
            "amount": 200000.0  # More than balance
        }
    )
    assert response.status_code == 400
    assert "Transfer failed" in response.json()["detail"]

def test_transfer_money_to_nonexistent_user():
    """Test transfer to non-existent user"""
    sender_headers = get_auth_headers("lonelysender", "lonelypass123")
    
    response = client.post(
        "/wallet/transfer",
        headers=sender_headers,
        json={
            "recipient_username": "nonexistentuser",
            "amount": 100.0
        }
    )
    assert response.status_code == 400
    assert "Transfer failed" in response.json()["detail"]

def test_transfer_money_to_self():
    """Test transfer to self (should fail)"""
    sender_headers = get_auth_headers("selftransfer", "selfpass123")
    
    response = client.post(
        "/wallet/transfer",
        headers=sender_headers,
        json={
            "recipient_username": "selftransfer",  # Same as sender
            "amount": 100.0
        }
    )
    assert response.status_code == 400
    assert "Transfer failed" in response.json()["detail"]
