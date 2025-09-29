from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone

class User(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    balance: float = Field(default=0.0)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    transactions: List['Transaction'] = Relationship(back_populates='user')
    items: List['Item'] = Relationship(back_populates='owner')

class Item(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    owner_id: Optional[int] = Field(default=None, foreign_key='user.id')
    
    owner: Optional[User] = Relationship(back_populates='items')

class Transaction(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    transaction_type: str  # 'topup', 'spend', 'transfer', 'purchase'
    description: str
    user_id: Optional[int] = Field(default=None, foreign_key='user.id')
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    user: Optional[User] = Relationship(back_populates='transactions')
