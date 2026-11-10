from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import Account, Transaction
from .repositories import AccountRepository

def deposit(session: Session, account_number: str, amount: float) -> None:
    if amount <= 0:
        raise ValueError("Deposit amount must be positive")
    repo = AccountRepository(session)
    account = repo.get_by_number(account_number)
    if not account:
        raise ValueError("Account not found")
    
    account.balance += amount
    session.add(Transaction(account_id=account.id, amount=amount, operation_type="deposit"))
    session.commit()

def withdraw(session: Session, account_number: str, amount: float) -> None:
    if amount <= 0:
        raise ValueError("Withdrawal amount must be positive")
    repo = AccountRepository(session)
    account = repo.get_by_number(account_number)
    if not account:
        raise ValueError("Account not found")
    if account.balance - amount < 0:
        raise ValueError("Insufficient funds. Negative balance forbidden.")
    
    account.balance -= amount
    session.add(Transaction(account_id=account.id, amount=amount, operation_type="withdraw"))
    session.commit()

def transfer_money(session: Session, from_acc: str, to_acc: str, amount: float) -> None:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    repo = AccountRepository(session)
    sender = repo.get_by_number(from_acc)
    receiver = repo.get_by_number(to_acc)
    
    if not sender or not receiver:
        raise ValueError("One or both accounts not found")
    if sender.balance - amount < 0:
        raise ValueError("Insufficient funds for transfer")
    
    try:
        sender.balance -= amount
        receiver.balance += amount
        
        session.add(Transaction(account_id=sender.id, amount=amount, operation_type="transfer_out"))
        session.add(Transaction(account_id=receiver.id, amount=amount, operation_type="transfer_in"))
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def get_total_funds(session: Session) -> float:
    result = session.scalar(select(func.sum(Account.balance)))
    return result or 0.0