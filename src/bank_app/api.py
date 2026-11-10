import asyncio
from collections.abc import Generator
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from bank_app.database import SessionLocal
from bank_app.models import Account, Transaction
from bank_app.repositories import AccountRepository, ClientRepository
from bank_app.services import deposit, withdraw, transfer_money
from bank_app.schemas import (
    ClientCreate, AccountCreate, AccountResponse, 
    TransactionResponse, AmountRequest, TransferRequest, AccountUpdate
)
from bank_app.external_api import fetch_batch_balances

app = FastAPI(title="Bank API", version="1.0.0")

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@app.post("/clients", status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientCreate, session: Session = Depends(get_session)):
    repo = ClientRepository(session)
    client = repo.add(data.name)
    return {"id": client.id, "name": client.name}

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(data: AccountCreate, session: Session = Depends(get_session)):
    repo = AccountRepository(session)
    if repo.get_by_number(data.account_number):
        raise HTTPException(status_code=409, detail="Account number already exists")
        
    account = Account(
        account_number=data.account_number,
        client_id=data.client_id,
        balance=data.initial_balance
    )
    return repo.add(account)

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, session: Session = Depends(get_session)):
    # Для прикладу шукаємо за ID, але репозиторій має метод get_by_number
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account_type(account_id: int, data: AccountUpdate, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.account_type = data.account_type
    session.commit()
    session.refresh(account)
    return account

@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return None

@app.get("/accounts/{account_id}/transactions", response_model=list[TransactionResponse])
async def get_transactions(account_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, le=100), session: Session = Depends(get_session)):
    # Приклад query parameters (skip, limit)
    transactions = session.query(Transaction).filter(Transaction.account_id == account_id).offset(skip).limit(limit).all()
    return transactions

@app.post("/accounts/{account_number}/deposit")
async def deposit_money(account_number: str, data: AmountRequest, session: Session = Depends(get_session)):
    try:
        deposit(session, account_number, data.amount)
        return {"status": "success", "message": "Deposited successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/{account_number}/withdraw")
async def withdraw_money(account_number: str, data: AmountRequest, session: Session = Depends(get_session)):
    try:
        withdraw(session, account_number, data.amount)
        return {"status": "success", "message": "Withdrawn successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transfers")
async def transfer(data: TransferRequest, session: Session = Depends(get_session)):
    try:
        transfer_money(session, data.from_account, data.to_account, data.amount)
        return {"status": "success", "message": "Transfer completed atomically"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/batch-balances")
async def batch_balances(account_numbers: list[str]):
    # Демонстрація асинхронності: Task, gather, Semaphore, HTTPX
    try:
        # Викликаємо зовнішню функцію, яка робить паралельні HTTP-запити
        results = await fetch_batch_balances(account_numbers, "http://127.0.0.1:8000")
        return results
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Batch operation timed out")