import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_auth_headers(username, password):
    """Helper function to get authentication headers"""
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "role": "user"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_transactions_empty():
    """Test getting transactions for new user"""
    headers = get_auth_headers("newuser", "newpass123")
    
    response = client.get("/transactions", headers=headers)
    assert response.status_code == 200
    assert response.json() == []  # No transactions yet

def test_get_transactions_after_activities():
    """Test getting transactions after various activities"""
    headers = get_auth_headers("activeuser", "activepass123")
    
    # Perform some activities to generate transactions
    client.post("/wallet/top-up", headers=headers, json={"amount": 1000.0})
    client.post("/wallet/spend", headers=headers, json={"amount": 500.0})
    
    # Get transactions
    response = client.get("/transactions", headers=headers)
    assert response.status_code == 200
    transactions = response.json()
    
    # Should have at least 2 transactions (top-up and spend)
    assert len(transactions) >= 2
    
    # Check transaction types
    transaction_types = [t["type"] for t in transactions]
    assert "top_up" in transaction_types
    assert "spend" in transaction_types
    
    # Check amounts
    top_up_tx = next(t for t in transactions if t["type"] == "top_up")
    spend_tx = next(t for t in transactions if t["type"] == "spend")
    assert top_up_tx["amount"] == 1000.0
    assert spend_tx["amount"] == -500.0

def test_transactions_after_transfer():
    """Test transactions after money transfer"""
    # Create sender and recipient
    sender_headers = get_auth_headers("transfersender", "transferpass123")
    
    client.post(
        "/auth/register",
        json={
            "username": "transferrecipient",
            "password": "transferpass123",
            "role": "user"
        }
    )
    
    # Perform transfer
    client.post(
        "/wallet/transfer",
        headers=sender_headers,
        json={
            "recipient_username": "transferrecipient",
            "amount": 300.0
        }
    )
    
    # Check sender's transactions
    response = client.get("/transactions", headers=sender_headers)
    assert response.status_code == 200
    sender_transactions = response.json()
    
    # Should have transfer transaction
    transfer_tx = next((t for t in sender_transactions if t["type"] == "transfer_out"), None)
    assert transfer_tx is not None
    assert transfer_tx["amount"] == -300.0

def test_transactions_after_purchase():
    """Test transactions after item purchase"""
    # Create item as admin first
    admin_headers = get_auth_headers("adminforpurchase", "adminpass123")
    # Update user to admin role (you might need to adjust this based on your auth setup)
    
    # For this test, let's assume we have an admin user
    # Create item
    create_response = client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Transaction Test Item",
            "price": 250.0,
            "stock_val": 3
        }
    )
    item_id = create_response.json()["id"]
    
    # Buy item
    buyer_headers = get_auth_headers("transactionbuyer", "buypass123")
    client.post(f"/items/buy/{item_id}", headers=buyer_headers)
    
    # Check transactions
    response = client.get("/transactions", headers=buyer_headers)
    assert response.status_code == 200
    transactions = response.json()
    
    # Should have purchase transaction
    purchase_tx = next((t for t in transactions if t["type"] == "purchase"), None)
    assert purchase_tx is not None
    assert purchase_tx["amount"] == -250.0
    assert purchase_tx["product_id"] == item_id

def test_transaction_isolation_between_users():
    """Test that users can only see their own transactions"""
    # User 1 performs some transactions
    user1_headers = get_auth_headers("user1", "user1pass123")
    client.post("/wallet/top-up", headers=user1_headers, json={"amount": 100.0})
    
    # User 2 performs different transactions
    user2_headers = get_auth_headers("user2", "user2pass123")
    client.post("/wallet/top-up", headers=user2_headers, json={"amount": 200.0})
    
    # Check that each user only sees their own transactions
    user1_response = client.get("/transactions", headers=user1_headers)
    user1_transactions = user1_response.json()
    
    user2_response = client.get("/transactions", headers=user2_headers)
    user2_transactions = user2_response.json()
    
    # Each should have their own transactions
    user1_amounts = [t["amount"] for t in user1_transactions if t["type"] == "top_up"]
    user2_amounts = [t["amount"] for t in user2_transactions if t["type"] == "top_up"]
    
    assert 100.0 in user1_amounts
    assert 200.0 in user2_amounts
    assert 200.0 not in user1_amounts  # User1 shouldn't see user2's transactions
    assert 100.0 not in user2_amounts  # User2 shouldn't see user1's transactions
