'''
CRUD operations for users, items, and transactions
'''

from sqlmodel import select
from src.database import get_session  # REMOVED THE DOT
from src.models import User, Item, Transaction  # REMOVED THE DOT
from src.auth import get_password_hash  # REMOVED THE DOT
from uuid import UUID
from fastapi import HTTPException, status
from typing import Tuple, Optional, List
import logging 

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_user(username: str, password: str, role: str = "user") -> dict:
    try:
        logger.debug(f"Attempting to create user: {username}, role: {role}")
        
        with get_session() as session:
            # Check if user already exists
            existing_user = session.exec(select(User).where(User.username == username)).first()
            if existing_user:
                logger.warning(f"Username already exists: {username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            # Hash the password
            logger.debug("Hashing password...")
            password_hash = get_password_hash(password)
            logger.debug("Password hashed successfully")
            
            # Create user
            user = User(
                username=username, 
                password_hash=password_hash, 
                role=role
            )
            logger.debug(f"User object created for: {username}")
            
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.debug(f"User created successfully with ID: {user.id}")
            
            # Return user data as a dictionary
            return {
                "id": user.id,
                "username": user.username,
                "wallet_bal": user.wallet_bal,
                "role": user.role
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

def create_clean_user(user: User) -> User:
    """Create a clean User object without session attachment"""
    return User(
        id=user.id,
        username=user.username,
        password_hash=user.password_hash,
        wallet_bal=user.wallet_bal,
        role=user.role
    )


def get_user_by_username(username: str) -> Optional[User]:
    with get_session() as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user:
            return create_clean_user(user)
        return None

def get_user_by_id(user_id: UUID) -> Optional[User]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            return create_clean_user(user)
        return None

def list_users() -> List[User]:
    with get_session() as session:
        return list(session.exec(select(User)).all())

def list_items() -> List[Item]:
    with get_session() as session:
        return list(session.exec(select(Item)).all())

def get_item_by_id(item_id: UUID) -> Optional[Item]:
    with get_session() as session:
        return session.get(Item, item_id)

def add_item(name: str, price: float, stock_val: int) -> Item:
    with get_session() as session:
        item = Item(name=name, price=price, stock_val=stock_val)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

def update_item_stock(item_id: UUID, new_stock: int) -> Optional[Item]:
    with get_session() as session:
        item = session.get(Item, item_id)
        if item:
            item.stock_val = new_stock
            session.add(item)
            session.commit()
            session.refresh(item)
        return item

def spend_money(user_id: UUID, amount: float) -> Tuple[Optional[User], Optional[Transaction]]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None, None
            
        if user.wallet_bal < amount:
            return None, None
        
        user.wallet_bal -= amount
        transaction = Transaction(
            user_id=user_id, 
            amount=-amount, 
            type="spend"
        )
        
        session.add(user)
        session.add(transaction)
        session.commit()
        session.refresh(user)
        session.refresh(transaction)
        
        return user, transaction

def top_up_wallet(user_id: UUID, amount: float) -> Tuple[Optional[User], Optional[Transaction]]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None, None
        
        user.wallet_bal += amount
        transaction = Transaction(
            user_id=user_id, 
            amount=amount, 
            type="top_up"
        )
        
        session.add(user)
        session.add(transaction)
        session.commit()
        session.refresh(user)
        session.refresh(transaction)
        
        return user, transaction

def transfer_money(sender_id: UUID, recipient_username: str, amount: float) -> Tuple[Optional[User], Optional[User], Optional[Transaction]]:
    with get_session() as session:
        sender = session.get(User, sender_id)
        recipient = session.exec(select(User).where(User.username == recipient_username)).first()
        
        if not sender or not recipient:
            return None, None, None
            
        if sender.id == recipient.id:
            return None, None, None
            
        if sender.wallet_bal < amount:
            return None, None, None
        
        # perform trf
        sender.wallet_bal -= amount
        recipient.wallet_bal += amount
        
        transaction = Transaction(
            user_id=sender_id,
            amount=-amount,
            type="transfer_out"
        )
        
        recipient_transaction = Transaction(
            user_id=recipient.id,
            amount=amount,
            type="transfer_in"
        )
        
        session.add(sender)
        session.add(recipient)
        session.add(transaction)
        session.add(recipient_transaction)
        session.commit()
        
        session.refresh(sender)
        session.refresh(recipient)
        session.refresh(transaction)
        
        return sender, recipient, transaction

def buy_item(user_id: UUID, item_id: UUID) -> Tuple[Optional[User], Optional[Item], Optional[Transaction]]:
    with get_session() as session:
        user = session.get(User, user_id)
        item = session.get(Item, item_id)
        
        if not user or not item:
            return None, None, None
            
        if user.wallet_bal < item.price:
            return None, None, None
            
        if item.stock_val <= 0:
            return None, None, None
        
        # process purchase
        user.wallet_bal -= item.price
        item.stock_val -= 1
        
        transaction = Transaction(
            user_id=user_id,
            product_id=item_id,
            amount=-item.price,
            type="purchase"
        )
        
        session.add(user)
        session.add(item)
        session.add(transaction)
        session.commit()
        
        session.refresh(user)
        session.refresh(item)
        session.refresh(transaction)
        
        return user, item, transaction

def get_user_transactions(user_id: UUID) -> List[Transaction]:
    with get_session() as session:
        return list(session.exec(select(Transaction).where(Transaction.user_id == user_id)).all())
