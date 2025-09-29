'''
pydantic schemas for request/response validation and serialization
'''

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

class UserSchema(BaseModel):
    id: str
    username: str
    wallet_bal: float
    role: str = "user"
    
    model_config = ConfigDict(from_attributes=True)

class ItemSchema(BaseModel):
    id: str
    name: str
    price: float = Field(ge=0)
    stock_val: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)

class TransactionSchema(BaseModel):
    id: str
    user_id: str  # Changed from Optional to required
    product_id: Optional[str] = None
    amount: float
    timestamp: datetime
    type: str

    model_config = ConfigDict(from_attributes=True)

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Optional[str] = "user"

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not re.match('^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "password": "StrongPass123",
                "role": "user"
            }
        }
    }

class ItemCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock_val: int = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sample Item",
                "price": 29.99,
                "stock_val": 100
            }
        }
    }

class UserLoginSchema(BaseModel):
    username: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "password": "StrongPass123"
            }
        }
    }

class SpendMoneySchema(BaseModel):
    amount: float = Field(gt=0, description="Amount to spend")

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 50.0
            }
        }
    }

class TransferMoneySchema(BaseModel):
    recipient_username: str
    amount: float = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "recipient_username": "janedoe",
                "amount": 50.0
            }
        }
    }

class TopUpWalletSchema(BaseModel):
    amount: float = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 100.0
            }
        }
    }