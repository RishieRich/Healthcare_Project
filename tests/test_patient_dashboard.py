import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from patient_dashboard import PatientDashboard


def test_add_total_expense_column():
    data = [
        [1] * 20,
        [2] * 20,
    ]
    df = pd.DataFrame(data, columns=[f"col{i}" for i in range(20)])
    result = PatientDashboard().add_total_expense_column(df)
    assert list(result['added_amt']) == [9, 18]

