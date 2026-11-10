import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from bank_app.analytics import heavy_risk_score, process_transactions_python

# ==========================================
# 1. Демонстрація Race Condition
# ==========================================
shared_counter = 0
counter_lock = threading.Lock()

def unsafe_increment():
    global shared_counter
    for _ in range(100000):
        # Тут виникає Race Condition
        shared_counter += 1

def safe_increment():
    global shared_counter
    for _ in range(100000):
        # Використання Lock (Synchronization)
        with counter_lock:
            shared_counter += 1

# ==========================================
# 2. ThreadPoolExecutor (для I/O або легких задач)
# ==========================================
def process_chunk_threads(transactions: list[dict]) -> float:
    return sum(heavy_risk_score(tx["amount"], 1000.0) for tx in transactions)

def process_threads(transactions: list[dict], workers: int = 4) -> float:
    chunk_size = len(transactions) // workers
    chunks = [transactions[i:i + chunk_size] for i in range(0, len(transactions), chunk_size)]
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_chunk_threads, chunks))
    return sum(results)

# ==========================================
# 3. ProcessPoolExecutor (для важких CPU-bound задач)
# ==========================================
def process_processes(transactions: list[dict], workers: int = 4) -> float:
    chunk_size = len(transactions) // workers
    chunks = [transactions[i:i + chunk_size] for i in range(0, len(transactions), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_chunk_threads, chunks))
    return sum(results)