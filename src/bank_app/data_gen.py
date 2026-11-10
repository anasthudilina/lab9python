import random

def generate_accounts(count: int) -> list[dict]:
    random.seed(42)
    return [
        {"id": i, "balance": random.uniform(100.0, 10000.0)}
        for i in range(1, count + 1)
    ]

def generate_transactions(accounts_count: int, tx_count: int) -> list[dict]:
    random.seed(43)
    return [
        {
            "account_id": random.randint(1, accounts_count),
            "amount": random.uniform(-500.0, 500.0),
            "type": random.choice(["deposit", "withdraw"])
        }
        for _ in range(tx_count)
    ]