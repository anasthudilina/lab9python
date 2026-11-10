import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cProfile
import pstats
import tracemalloc
import os
from time import perf_counter
from bank_app.data_gen import generate_transactions
from bank_app.analytics import process_transactions_python, process_transactions_numpy
from bank_app.parallel import process_threads, process_processes, unsafe_increment, safe_increment
import bank_app.parallel as parallel
import threading  

def measure_time(func, *args) -> float:
    start = perf_counter()
    func(*args)
    return perf_counter() - start

def main():
    # 1. Підготовка даних (згідно з вимогами: 100 000+ рахунків, 500 000+ операцій)
    # Для швидкості вашого комп'ютера ми беремо 100 000 операцій. 
    # Для звіту можете збільшити до 500 000.
    TX_COUNT = 100_000 
    transactions = generate_transactions(100_000, TX_COUNT)
    
    print(f"--- Benchmark for {TX_COUNT} transactions ---")
    
    # 2. Вимірювання часу (perf_counter)
    time_python = measure_time(process_transactions_python, transactions)
    time_numpy = measure_time(process_transactions_numpy, transactions)
    time_threads = measure_time(process_threads, transactions, 4)
    time_processes = measure_time(process_processes, transactions, 4)
    
    print(f"Python Baseline : {time_python:.4f} s")
    print(f"NumPy           : {time_numpy:.4f} s (Speedup: {time_python/time_numpy:.2f}x)")
    print(f"ThreadPool      : {time_threads:.4f} s (Speedup: {time_python/time_threads:.2f}x)")
    print(f"ProcessPool     : {time_processes:.4f} s (Speedup: {time_python/time_processes:.2f}x)")

    # 3. cProfile для пошуку bottleneck
    print("\n--- cProfile Results ---")
    profiler = cProfile.Profile()
    profiler.enable()
    process_transactions_python(transactions)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(3) # Показуємо топ-3 функцій
    
    # 4. tracemalloc (аналіз пам'яті)
    print("\n--- tracemalloc Results ---")
    tracemalloc.start()
    process_transactions_python(transactions)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    tracemalloc.stop()

    # 5. Race Condition та Synchronization
    print("\n--- Race Condition Demo ---")
    
    # Безпечний запуск (очікуємо 200 000)
    parallel.shared_counter = 0
    t1 = threading.Thread(target=safe_increment)
    t2 = threading.Thread(target=safe_increment)
    t1.start(); t2.start()
    t1.join(); t2.join()
    print(f"Safe counter with Lock: {parallel.shared_counter}")
    
    # Небезпечний запуск (очікуємо 200 000, але буде менше)
    parallel.shared_counter = 0
    t3 = threading.Thread(target=unsafe_increment)
    t4 = threading.Thread(target=unsafe_increment)
    t3.start(); t4.start()
    t3.join(); t4.join()
    print(f"Unsafe counter (Race Condition): {parallel.shared_counter}")

if __name__ == "__main__":
    main()