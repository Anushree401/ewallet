# 🏪 E-Commerce Wallet API - Complete Documentation

## 📋 Project Overview
A **FastAPI-based e-commerce system** with integrated wallet functionality, JWT authentication, and comprehensive transaction management.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Setup

1. **Clone and Setup Environment**
```bash
# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlmodel python-dotenv python-jose passlib[bcrypt]
```

2. **Environment Configuration**
Create `.env` file:
```env
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite:///./test.db
```

3. **Run the Application**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. Register New User
**Creates a new user account with initial wallet balance**

```bash
# Using curl
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "password": "SecurePass123",
       "role": "user"
     }'
```

**Postman Setup:**
- **Method**: POST
- **URL**: `http://localhost:8000/auth/register`
- **Body** (raw JSON):
```json
{
    "username": "john_doe",
    "password": "SecurePass123",
    "role": "user"
}
```

**Success Response (201 Created):**
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "john_doe",
    "wallet_bal": 1000.0,
    "role": "user"
}
```

### 2. User Login
**Authenticates user and returns JWT token**

```bash
# Using curl
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "password": "SecurePass123"
     }'
```

**Postman Setup:**
- **Method**: POST
- **URL**: `http://localhost:8000/auth/login`
- **Body** (raw JSON):
```json
{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

**Success Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**💡 Save this token for all subsequent authenticated requests!**

---

## 👤 USER PROFILE & WALLET ENDPOINTS

*All these endpoints require JWT authentication*

### 3. Get User Profile
```bash
# Using curl
curl -X GET "http://localhost:8000/users/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Postman Setup:**
- **Method**: GET
- **URL**: `http://localhost:8000/users/me`
- **Headers**: 
  - `Authorization: Bearer YOUR_ACCESS_TOKEN`

### 4. Get Wallet Balance
```bash
curl -X GET "http://localhost:8000/wallet/balance" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Top Up Wallet
**Add money to user's wallet**

```bash
curl -X POST "http://localhost:8000/wallet/top-up" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"amount": 500.0}'
```

**Postman Body:**
```json
{
    "amount": 500.0
}
```

### 6. Spend Money
**Deduct money from wallet (generic spending)**

```bash
curl -X POST "http://localhost:8000/wallet/spend" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"amount": 150.0}'
```

### 7. Transfer Money to Another User
**Send money to another user by username**

```bash
curl -X POST "http://localhost:8000/wallet/transfer" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "recipient_username": "jane_smith",
       "amount": 200.0
     }'
```

**Postman Body:**
```json
{
    "recipient_username": "jane_smith",
    "amount": 200.0
}
```

**Success Response:**
```json
{
    "message": "Transfer successful",
    "sender_balance": 800.0,
    "recipient": "jane_smith"
}
```

### 8. Get Transaction History
```bash
curl -X GET "http://localhost:8000/transactions" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
[
    {
        "id": "txn-123",
        "user_id": "user-123",
        "product_id": null,
        "amount": 500.0,
        "timestamp": "2024-01-15T10:30:00Z",
        "type": "top_up"
    },
    {
        "id": "txn-124",
        "user_id": "user-123",
        "product_id": "item-456",
        "amount": -150.0,
        "timestamp": "2024-01-15T11:15:00Z",
        "type": "purchase"
    }
]
```

---

## 🛍️ PRODUCT CATALOG ENDPOINTS

### 9. Browse All Items
**Public endpoint - no authentication required**

```bash
curl -X GET "http://localhost:8000/items"
```

### 10. Get Specific Item Details
```bash
curl -X GET "http://localhost:8000/items/ITEM_ID_HERE"
```

### 11. Purchase an Item
**Buy an item using wallet balance**

```bash
curl -X POST "http://localhost:8000/items/buy/ITEM_ID_HERE" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response:**
```json
{
    "message": "Purchase successful",
    "user": {
        "id": "user-123",
        "username": "john_doe",
        "wallet_bal": 650.0,
        "role": "user"
    },
    "item": {
        "id": "item-456",
        "name": "Wireless Headphones",
        "price": 150.0,
        "stock_val": 9
    },
    "transaction": {
        "id": "txn-125",
        "user_id": "user-123",
        "product_id": "item-456",
        "amount": -150.0,
        "timestamp": "2024-01-15T11:20:00Z",
        "type": "purchase"
    }
}
```

---

## 👑 ADMIN ENDPOINTS

*Requires admin role in JWT token*

### 12. Create New Item (Admin Only)
```bash
curl -X POST "http://localhost:8000/admin/items" \
     -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Gaming Laptop",
       "price": 1299.99,
       "stock_val": 10
     }'
```

**Postman Body:**
```json
{
    "name": "Gaming Laptop",
    "price": 1299.99,
    "stock_val": 10
}
```

### 13. List All Users (Admin Only)
```bash
curl -X GET "http://localhost:8000/admin/users" \
     -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

---

## 🩺 HEALTH & DEBUGGING ENDPOINTS

### 14. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### 15. Test Database Connection
```bash
curl -X POST "http://localhost:8000/test-db"
```

### 16. Check User Existence
```bash
curl -X GET "http://localhost:8000/test-get-user/john_doe"
```

---

## 🔄 COMPLETE WORKFLOW EXAMPLES

### Example 1: Complete Shopping Experience

```bash
# 1. Register (if new user)
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"shopper1","password":"pass123","role":"user"}'

# 2. Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"shopper1","password":"pass123"}' | jq -r '.access_token')

# 3. Check balance
curl -X GET "http://localhost:8000/wallet/balance" \
     -H "Authorization: Bearer $TOKEN"

# 4. Browse items
curl -X GET "http://localhost:8000/items"

# 5. Purchase item (replace ITEM_ID with actual ID)
curl -X POST "http://localhost:8000/items/buy/ITEM_ID" \
     -H "Authorization: Bearer $TOKEN"

# 6. Check transaction history
curl -X GET "http://localhost:8000/transactions" \
     -H "Authorization: Bearer $TOKEN"
```

### Example 2: Money Transfer Between Users

```bash
# User A transfers to User B

# User A login
TOKEN_A=$(curl -s -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"user_a","password":"pass123"}' | jq -r '.access_token')

# Transfer money to User B
curl -X POST "http://localhost:8000/wallet/transfer" \
     -H "Authorization: Bearer $TOKEN_A" \
     -H "Content-Type: application/json" \
     -d '{"recipient_username":"user_b","amount":100.0}'
```

---

## 🛡️ AUTHENTICATION FLOW

### How JWT Tokens Work:
1. **Login** → Get JWT token containing user identity and role
2. **Subsequent Requests** → Include token in `Authorization: Bearer <token>` header
3. **Server Validates** → Decodes token, verifies signature, checks expiration
4. **Access Control** → Admin endpoints require `is_admin: true` in token

### Token Structure (Decoded):
```json
{
  "sub": "john_doe",
  "is_admin": false,
  "exp": 1730000000
}
```

---

## 💰 TRANSACTION TYPES

| Type | Amount | Description |
|------|--------|-------------|
| `top_up` | Positive | Adding money to wallet |
| `spend` | Negative | Generic spending |
| `purchase` | Negative | Buying specific item |
| `transfer_out` | Negative | Sending money to another user |
| `transfer_in` | Positive | Receiving money from another user |

---

## ⚠️ ERROR HANDLING

### Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors, insufficient funds)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

### Example Error Responses:
```json
{
    "detail": "Insufficient funds"
}
```
```json
{
    "detail": "Could not validate credentials"
}
```

---

## 📊 DEFAULT CONFIGURATION

- **Initial User Balance**: 1000.0
- **Token Expiration**: 30 minutes
- **Password Requirements**: Minimum 8 characters
- **Username Requirements**: Alphanumeric + underscore, 3-50 characters

---

## 🔧 TROUBLESHOOTING

### Common Issues:

1. **"Could not validate credentials"**
   - Token expired or invalid
   - Missing Authorization header

2. **"Insufficient funds"**
   - Wallet balance less than requested amount

3. **"Username already registered"**
   - Username must be unique

4. **"Item not found"**
   - Invalid item ID

### Debug Tools:
- Check `/health` endpoint
- Use `/test-db` to verify database connection
- Check server logs for detailed errors

---

## 🚀 PRODUCTION DEPLOYMENT NOTES

1. **Change SECRET_KEY** in production
2. **Use PostgreSQL** instead of SQLite
3. **Set proper CORS** origins
4. **Use environment variables** for all configurations
5. **Implement rate limiting**
6. **Add proper logging** and monitoring

This API provides a complete e-commerce experience with secure wallet functionality, user management, and comprehensive transaction tracking!