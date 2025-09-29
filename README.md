# E-Wallet API - TQ Documentation

## 📋 Overview
A FastAPI-based e-commerce API with user wallet functionality, authentication, and transaction management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup**
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-change-in-production
```

5. **Run the application**
```bash
uvicorn src.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

## 📚 API Endpoints

### 🔐 Authentication Endpoints

#### POST `/auth/register`
Register a new user.

**Request:**
```json
{
    "username": "johndoe",
    "password": "password123",
    "role": "user"
}
```

**Response:**
```json
{
    "id": "uuid",
    "username": "johndoe",
    "wallet_bal": 100000.0,
    "role": "user"
}
```

#### POST `/auth/login`
Login and get access token.

**Request:**
```json
{
    "username": "johndoe",
    "password": "password123"
}
```

**Response:**
```json
{
    "access_token": "jwt-token",
    "token_type": "bearer"
}
```

### 👤 User Endpoints (Require Authentication)

#### GET `/users/me`
Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

#### GET `/wallet/balance`
Get current wallet balance.

#### POST `/wallet/top-up`
Add money to wallet.

**Request:**
```json
{
    "amount": 100.0
}
```

#### POST `/wallet/spend`
Spend money from wallet.

**Request:**
```json
{
    "amount": 50.0
}
```

#### POST `/wallet/transfer`
Transfer money to another user.

**Request:**
```json
{
    "recipient_username": "janedoe",
    "amount": 25.0
}
```

#### GET `/transactions`
Get user's transaction history.

### 🛍️ Item Endpoints

#### GET `/items`
Get all available items.

#### GET `/items/{item_id}`
Get specific item details.

#### POST `/items/buy/{item_id}`
Purchase an item.

### 👑 Admin Endpoints (Require Admin Role)

#### POST `/admin/items`
Create new item (Admin only).

**Request:**
```json
{
    "name": "Laptop",
    "price": 999.99,
    "stock_val": 10
}
```

#### GET `/admin/users`
List all users (Admin only).

### 🩺 Health & Debug Endpoints

#### GET `/health`
Check API status.

#### POST `/test-db`
Test database connection.

#### GET `/test-get-user/{username}`
Check if user exists.

## 🔐 Authentication

### How to Use Authentication:

1. **Register a user:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass123","role":"user"}'
```

2. **Login to get token:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass123"}'
```

3. **Use token in requests:**
```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🗄️ Database Models

### User
- `id`: UUID (Primary Key)
- `username`: String (Unique)
- `password_hash`: String
- `wallet_bal`: Float (Default: 100,000.0)
- `role`: String ('user' or 'admin')

### Item
- `id`: UUID (Primary Key)
- `name`: String
- `price`: Float
- `stock_val`: Integer

### Transaction
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `product_id`: UUID (Foreign Key, Optional)
- `amount`: Float
- `timestamp`: DateTime
- `type`: String ('purchase', 'transfer', 'refund', etc.)

## 🛠️ Development

### Project Structure
```
backend/
├── src/
│   ├── main.py          # FastAPI application & endpoints
│   ├── models.py        # Database models
│   ├── schema.py        # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # Authentication & authorization
│   └── database.py      # Database connection
├── requirements.txt
└── .env
```

### Running Tests
```bash
# Test database connection
curl -X POST "http://127.0.0.1:8000/test-db"

# Test user creation
curl -X GET "http://127.0.0.1:8000/test-get-user/username"
```

## 📊 Default Data

- New users start with **100,000.0** wallet balance
- Default user role is **"user"**
- Admin users can be created with `"role": "admin"`

---

# 📁 How to Put on GitHub

## Step 1: Prepare Your Project

1. **Create necessary files:**

   `requirements.txt`
   ```txt
   fastapi==0.104.1
   uvicorn==0.24.0
   sqlmodel==0.0.14
   python-dotenv==1.0.0
   python-jose==3.3.0
   passlib[bcrypt]==1.7.4
   sqlalchemy==2.0.23
   ```

   `.gitignore`
   ```gitignore
   # Python
   __pycache__/
   *.pyc
   *.pyo
   *.pyd
   .Python
   env/
   venv/
   
   # Database
   *.db
   *.sqlite3
   
   # Environment
   .env
   
   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo
   ```

## Step 2: Initialize Git Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: E-Wallet API with FastAPI and SQLModel"
```

## Step 3: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "+" → "New repository"
3. Name: `e-wallet-api`
4. Description: "A FastAPI-based e-commerce API with user wallet functionality"
5. Choose Public/Private
6. **Don't** initialize with README (we'll add ours)

## Step 4: Connect and Push

```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/e-wallet-api.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 5: Add Project Details (Optional)

Create `README.md` in your project root with the documentation above.

## 🚀 Deployment Ready Features

- **Environment variables** for configuration
- **Database migrations** ready
- **JWT authentication** implemented
- **Role-based access control**
- **Comprehensive error handling**
- **API documentation** auto-generated at `/docs`

## 📝 API Documentation

Visit `http://127.0.0.1:8000/docs` for interactive Swagger documentation after running the application.

## 🔧 Troubleshooting

### Common Issues:

1. **Database connection error**: Check `.env` file and database URL
2. **Import errors**: Ensure you're in the correct directory and virtual environment is activated
3. **Authentication errors**: Verify JWT token is included in Authorization header
4. **Permission errors**: Check user role for admin endpoints

### Debug Endpoints:
- `/health` - API status
- `/test-db` - Database connection test
- `/test-get-user/{username}` - User existence check

This API provides a complete e-wallet system with user management, transactions, and inventory management!