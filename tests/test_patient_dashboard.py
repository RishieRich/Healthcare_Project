import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from patient_dashboard import PatientDashboard


def test_add_total_expense_column_with_prefix():
    df = pd.DataFrame(
        {
            "registrationno": [1, 2],
            "expense_room": ["100", 200],
            "expense_medicine": [50.5, "invalid"],
            "expense_misc": [None, 25],
            "non_expense": [10, 20],
        }
    )

    result = PatientDashboard().add_total_expense_column(df)

    assert list(result["added_amt"]) == [150.5, 225.0]


def test_add_total_expense_column_missing_required_column():
    df = pd.DataFrame(
        {
            "registrationno": [1],
            "expense_room": [100],
        }
    )

    dashboard = PatientDashboard()

    with pytest.raises(ValueError) as exc:
        dashboard.add_total_expense_column(df, expense_columns=["expense_room", "expense_food"])

    assert "expense_food" in str(exc.value)

