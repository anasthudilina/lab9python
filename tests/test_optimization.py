import pytest
from bank_app.data_gen import generate_transactions
from bank_app.analytics import process_transactions_python, process_transactions_numpy
from bank_app.parallel import process_processes

def test_optimization_correctness():
    txs = generate_transactions(10, 50)
    
    res_python = process_transactions_python(txs)
    res_numpy = process_transactions_numpy(txs)
    res_proc = process_processes(txs, workers=2)
    
    # Перевіряємо, чи однакові результати (з похибкою float)
    assert res_numpy == pytest.approx(res_python, rel=1e-4)
    assert res_proc == pytest.approx(res_python, rel=1e-4)