import sqlite3
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Client, Account

class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str) -> Client:
        client = Client(name=name)
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, account: Account) -> Account:
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_by_number(self, number: str) -> Account | None:
        statement = select(Account).where(Account.account_number == number)
        return self.session.scalar(statement)

    def get_all(self) -> list[Account]:
        return list(self.session.scalars(select(Account)))

    def update_balance(self, account: Account, new_balance: float) -> None:
        account.balance = new_balance
        self.session.commit()

    def delete(self, account: Account) -> None:
        self.session.delete(account)
        self.session.commit()

# Демонстрація DB-API (без ORM)
def dbapi_find_account_by_number(db_path: str, account_number: str) -> tuple | None:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        # Параметризований запит для захисту від SQL Injection
        cursor.execute(
            "SELECT account_number, balance FROM accounts WHERE account_number = ?", 
            (account_number,)
        )
        return cursor.fetchone()