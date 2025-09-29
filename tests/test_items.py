import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid

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

def get_admin_headers():
    """Helper function to get admin authentication headers"""
    client.post(
        "/auth/register",
        json={
            "username": "adminuser",
            "password": "adminpass123",
            "role": "admin"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "username": "adminuser",
            "password": "adminpass123"
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_items_empty():
    """Test getting items when no items exist"""
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []

def test_create_item_as_admin():
    """Test creating item as admin"""
    headers = get_admin_headers()
    
    response = client.post(
        "/admin/items",
        headers=headers,
        json={
            "name": "Test Laptop",
            "price": 999.99,
            "stock_val": 10
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["price"] == 999.99
    assert data["stock_val"] == 10
    assert "id" in data

def test_create_item_as_regular_user():
    """Test creating item as regular user (should fail)"""
    headers = get_auth_headers("regularuser", "regularpass123")
    
    response = client.post(
        "/admin/items",
        headers=headers,
        json={
            "name": "Unauthorized Item",
            "price": 100.0,
            "stock_val": 5
        }
    )
    assert response.status_code == 403  # Forbidden
    assert "Insufficient permissions" in response.json()["detail"]

def test_get_items_list():
    """Test getting list of items"""
    # First create some items
    admin_headers = get_admin_headers()
    client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Item 1",
            "price": 100.0,
            "stock_val": 5
        }
    )
    client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Item 2",
            "price": 200.0,
            "stock_val": 3
        }
    )
    
    # Get items
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(item["name"] == "Item 1" for item in data)
    assert any(item["name"] == "Item 2" for item in data)

def test_get_specific_item():
    """Test getting a specific item by ID"""
    # Create an item first
    admin_headers = get_admin_headers()
    create_response = client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Specific Item",
            "price": 150.0,
            "stock_val": 8
        }
    )
    item_id = create_response.json()["id"]
    
    # Get the specific item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Specific Item"
    assert data["price"] == 150.0
    assert data["stock_val"] == 8

def test_get_nonexistent_item():
    """Test getting a non-existent item"""
    fake_id = uuid.uuid4()
    response = client.get(f"/items/{fake_id}")
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]

def test_buy_item_success():
    """Test successful item purchase"""
    # Create an item
    admin_headers = get_admin_headers()
    create_response = client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Buyable Item",
            "price": 500.0,
            "stock_val": 5
        }
    )
    item_id = create_response.json()["id"]
    
    # Buy the item
    user_headers = get_auth_headers("buyeruser", "buyerpass123")
    response = client.post(
        f"/items/buy/{item_id}",
        headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Purchase successful"
    assert data["user"]["wallet_bal"] == 99500.0  # 100000 - 500
    assert data["item"]["stock_val"] == 4  # 5 - 1

def test_buy_item_insufficient_funds():
    """Test buying item with insufficient funds"""
    # Create expensive item
    admin_headers = get_admin_headers()
    create_response = client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Expensive Item",
            "price": 200000.0,  # More than default balance
            "stock_val": 1
        }
    )
    item_id = create_response.json()["id"]
    
    # Try to buy (should fail)
    user_headers = get_auth_headers("poorbuyer", "poorpass123")
    response = client.post(
        f"/items/buy/{item_id}",
        headers=user_headers
    )
    assert response.status_code == 400
    assert "Purchase failed" in response.json()["detail"]

def test_buy_out_of_stock_item():
    """Test buying out-of-stock item"""
    # Create item with zero stock
    admin_headers = get_admin_headers()
    create_response = client.post(
        "/admin/items",
        headers=admin_headers,
        json={
            "name": "Out of Stock Item",
            "price": 100.0,
            "stock_val": 0  # No stock
        }
    )
    item_id = create_response.json()["id"]
    
    # Try to buy (should fail)
    user_headers = get_auth_headers("stockbuyer", "stockpass123")
    response = client.post(
        f"/items/buy/{item_id}",
        headers=user_headers
    )
    assert response.status_code == 400
    assert "Purchase failed" in response.json()["detail"]

def test_buy_nonexistent_item():
    """Test buying non-existent item"""
    user_headers = get_auth_headers("fakebuyer", "fakepass123")
    fake_id = uuid.uuid4()
    
    response = client.post(
        f"/items/buy/{fake_id}",
        headers=user_headers
    )
    assert response.status_code == 400
    assert "Purchase failed" in response.json()["detail"]
