'''
pydantic schemas for request/response validation and serialization
'''

from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime
import re

class UserSchema(BaseModel):
    id: UUID
    username: str
    wallet_bal: float
    role: str = "user"
    
    model_config = ConfigDict(from_attributes=True)
# class UserSchema(BaseModel):
#     id: UUID
#     username: str
#     wallet_bal: float
#     role: str = "user"
    
#     class Config:
#         from_attributes = True

class ItemSchema(BaseModel):
    id: UUID
    name: str
    price: float = Field(ge=0)
    stock_val: int = Field(ge=0)

    class Config:
        from_attributes = True

class TransactionSchema(BaseModel):
    id: UUID
    user_id: UUID
    product_id: Optional[UUID] = None
    amount: float
    timestamp: datetime
    type: str

    class Config:
        from_attributes = True

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
        # if not any(c.isupper() for c in v):
        #     raise ValueError('Password must contain at least one uppercase letter')
        # if not any(c.islower() for c in v):
        #     raise ValueError('Password must contain at least one lowercase letter')
        # if not any(c.isdigit() for c in v):
        #     raise ValueError('Password must contain at least one digit')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "StrongPass123",
                "role": "user"
            }
        }

class ItemCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock_val: int = Field(ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sample Item",
                "price": 29.99,
                "stock_val": 100
            }
        }

class UserLoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "StrongPass123"
            }
        }

class SpendMoneySchema(BaseModel):
    amount: float = Field(gt=0, description="Amount to spend")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 50.0
            }
        }

class TransferMoneySchema(BaseModel):
    recipient_username: str
    amount: float = Field(gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_username": "janedoe",
                "amount": 50.0
            }
        }

class TopUpWalletSchema(BaseModel):
    amount: float = Field(gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.0
            }
        }
