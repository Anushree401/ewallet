from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class User(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    balance: float = Field(default=0.0)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    transactions: List["Transaction"] = Relationship(back_populates="user")
    items: List["Item"] = Relationship(back_populates="owner")

class Item(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    price: float
    stock_val: int = Field(default=0)
    owner_id: Optional[str] = Field(default=None, foreign_key="user.id")
    
    owner: Optional[User] = Relationship(back_populates="items")

class Transaction(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    amount: float
    transaction_type: str  # 'top_up', 'spend', 'transfer_out', 'transfer_in', 'purchase'
    user_id: str = Field(foreign_key="user.id")  # Changed from Optional to required
    product_id: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    user: Optional[User] = Relationship(back_populates="transactions")