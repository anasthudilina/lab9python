import math
import numpy as np

def heavy_risk_score(amount: float, balance: float) -> float:
    """Імітація важкого CPU-bound обчислення"""
    val = abs(amount) + abs(balance) + 1.0
    for _ in range(50):
        val = math.sin(val) ** 2 + math.cos(val) ** 2 + math.sqrt(val)
    return val

def process_transactions_python(transactions: list[dict]) -> float:
    """Baseline: звичайний цикл Python"""
    total_score = 0.0
    for tx in transactions:
        total_score += heavy_risk_score(tx["amount"], tx.get("balance", 1000.0))
    return total_score

def process_transactions_numpy(transactions: list[dict]) -> float:
    """Оптимізація через NumPy (векторизація)"""
    if not transactions:
        return 0.0
        
    amounts = np.array([tx["amount"] for tx in transactions], dtype=np.float64)
    balances = np.full(len(transactions), 1000.0, dtype=np.float64)
    
    val = np.abs(amounts) + np.abs(balances) + 1.0
    for _ in range(50):
        val = np.sin(val) ** 2 + np.cos(val) ** 2 + np.sqrt(val)
    
    return float(np.sum(val))