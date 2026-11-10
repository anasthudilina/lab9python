import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_app.database import engine, SessionLocal
from bank_app.models import Base, Account
from bank_app.repositories import ClientRepository, AccountRepository
from bank_app.services import deposit, withdraw, transfer_money, get_total_funds

def main() -> None:
    Base.metadata.create_all(engine)
    
    with SessionLocal() as session:
        client_repo = ClientRepository(session)
        acc_repo = AccountRepository(session)
        
        # Створення клієнтів
        alice = client_repo.add("Alice")
        bob = client_repo.add("Bob")
        
        # Створення рахунків
        acc1 = acc_repo.add(Account(account_number="UA001", client_id=alice.id, balance=1000.0))
        acc2 = acc_repo.add(Account(account_number="UA002", client_id=bob.id, balance=500.0))
        
        print(f"Total funds before: {get_total_funds(session)}")
        
        # Транзакція переказу
        transfer_money(session, "UA001", "UA002", 300.0)
        
        print(f"Total funds after: {get_total_funds(session)}")
        print(f"Alice balance: {acc_repo.get_by_number('UA001').balance}")
        print(f"Bob balance: {acc_repo.get_by_number('UA002').balance}")

if __name__ == "__main__":
    main()