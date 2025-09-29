from sqlmodel import select
from src.database import get_session
from src.models import User, Item, Transaction
from src.auth import get_password_hash
from fastapi import HTTPException, status
from typing import Tuple, Optional, List
import logging 
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_user(username: str, password: str, role: str = "user") -> dict:
    try:
        logger.debug(f"Attempting to create user: {username}, role: {role}")

        session = next(get_session())
        try:
            existing_user = session.exec(select(User).where(User.username == username)).first()
            if existing_user:
                logger.warning(f"Username already exists: {username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
    
            logger.debug("Hashing password...")
            password_hash = get_password_hash(password)
            logger.debug("Password hashed successfully")
    
            is_admin = role == "admin"
            user = User(
                username=username,
                email=f"{username}@example.com",
                hashed_password=password_hash,
                balance=1000.0,
                is_admin=is_admin
            )
            logger.debug(f"User object created for: {username}")
    
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.debug(f"User created successfully with ID: {user.id}")
    
            return {
                "id": user.id,
                "username": user.username,
                "wallet_bal": user.balance,
                "role": "admin" if user.is_admin else "user"
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

def create_clean_user(user: User) -> User:
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        balance=user.balance,
        is_admin=user.is_admin,
        created_at=user.created_at
    )

def get_user_by_username(username: str) -> Optional[User]:
    session = next(get_session())
    try:
        user = session.exec(select(User).where(User.username == username)).first()
        if user:
            return create_clean_user(user)
        return None
    finally:
        session.close()

def get_user_by_id(user_id: str) -> Optional[User]:
    session = next(get_session())
    try:
        user = session.get(User, user_id)
        if user:
            return create_clean_user(user)
        return None
    finally:
        session.close()

def list_users() -> List[User]:
    session = next(get_session())
    try:
        users = session.exec(select(User)).all()
        return [create_clean_user(user) for user in users]
    finally:
        session.close()

def list_items() -> List[Item]:
    session = next(get_session())
    try:
        return list(session.exec(select(Item)).all())
    finally:
        session.close()

def get_item_by_id(item_id: str) -> Optional[Item]:
    session = next(get_session())
    try:
        return session.get(Item, item_id)
    finally:
        session.close()

def add_item(name: str, price: float, stock_val: int) -> Item:
    session = next(get_session())
    try:
        item = Item(name=name, price=price, stock_val=stock_val)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    finally:
        session.close()

def update_item_stock(item_id: str, new_stock: int) -> Optional[Item]:
    session = next(get_session())
    try:
        item = session.get(Item, item_id)
        if item:
            item.stock_val = new_stock
            session.add(item)
            session.commit()
            session.refresh(item)
        return item
    finally:
        session.close()

def spend_money(user_id: str, amount: float) -> Tuple[Optional[User], Optional[Transaction]]:
    session = next(get_session())
    try:
        user = session.get(User, user_id)
        if not user or user.balance < amount:
            return None, None
        
        user.balance -= amount
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,
            transaction_type="spend"
        )
        session.add(user)
        session.add(transaction)
        session.commit()
        session.refresh(user)
        session.refresh(transaction)
        return user, transaction
    finally:
        session.close()

def top_up_wallet(user_id: str, amount: float) -> Tuple[Optional[User], Optional[Transaction]]:
    session = next(get_session())
    try:
        user = session.get(User, user_id)
        if not user:
            return None, None
        
        user.balance += amount
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type="top_up"
        )
        session.add(user)
        session.add(transaction)
        session.commit()
        session.refresh(user)
        session.refresh(transaction)
        return user, transaction
    finally:
        session.close()

def transfer_money(sender_id: str, recipient_username: str, amount: float) -> Tuple[Optional[User], Optional[User], Optional[Transaction]]:
    session = next(get_session())
    try:
        sender = session.get(User, sender_id)
        recipient = session.exec(select(User).where(User.username == recipient_username)).first()
        if not sender or not recipient or sender.id == recipient.id or sender.balance < amount:
            return None, None, None
        
        sender.balance -= amount
        recipient.balance += amount
        
        transaction = Transaction(
            user_id=sender_id,
            amount=-amount,
            transaction_type="transfer_out"
        )
        recipient_transaction = Transaction(
            user_id=recipient.id,
            amount=amount,
            transaction_type="transfer_in"
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
    finally:
        session.close()

def buy_item(user_id: str, item_id: str) -> Tuple[Optional[User], Optional[Item], Optional[Transaction]]:
    session = next(get_session())
    try:
        user = session.get(User, user_id)
        item = session.get(Item, item_id)
        if not user or not item or user.balance < item.price or item.stock_val <= 0:
            return None, None, None
        
        user.balance -= item.price
        item.stock_val -= 1
        
        transaction = Transaction(
            user_id=user_id,
            product_id=item_id,
            amount=-item.price,
            transaction_type="purchase"
        )
        session.add(user)
        session.add(item)
        session.add(transaction)
        session.commit()
        session.refresh(user)
        session.refresh(item)
        session.refresh(transaction)
        return user, item, transaction
    finally:
        session.close()

def get_user_transactions(user_id: str) -> List[Transaction]:
    session = next(get_session())
    try:
        return list(session.exec(select(Transaction).where(Transaction.user_id == user_id)).all())
    finally:
        session.close()