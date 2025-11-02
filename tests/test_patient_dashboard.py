import os
import sys
import pandas as pd
import pytest

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


def _build_patient_df(expense_rows, added_amt=None):
    columns = [
        "registrationno",
        "patientname",
        "phone",
        "department",
        "misc4",
        "misc5",
        "misc6",
        "misc7",
        "misc8",
        "misc9",
        "misc10",
    ] + [f"expense{i}" for i in range(1, 10)]

    data = []
    for idx, expenses in enumerate(expense_rows):
        row = [
            f"REG{idx}",
            f"Patient {idx}",
            f"555000{idx}",
            "Cardiology" if idx % 2 == 0 else "Neurology",
        ]
        row += [f"misc_{idx}_{i}" for i in range(7)]
        row += list(expenses)
        data.append(row)

    df = pd.DataFrame(data, columns=columns)
    if added_amt is not None:
        df["added_amt"] = added_amt
    return df


def test_fetch_patient_phone_top_case_insensitive_order():
    expenses = [
        [100, 0, 0, 0, 0, 0, 0, 0, 0],
        [50, 0, 0, 0, 0, 0, 0, 0, 0],
        [200, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    df = _build_patient_df(expenses)
    result = PatientDashboard().fetch_patient_phone(df, "TOP_10")
    assert list(result["registrationno"]) == ["REG2", "REG0", "REG1"]


def test_fetch_patient_phone_bottom_order():
    expenses = [
        [200, 10, 0, 0, 0, 0, 0, 0, 0],
        [50, 0, 0, 0, 0, 0, 0, 0, 0],
        [150, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    df = _build_patient_df(expenses)
    result = PatientDashboard().fetch_patient_phone(df, "bottom_10")
    assert list(result["registrationno"]) == ["REG1", "REG2", "REG0"]


def test_fetch_patient_phone_invalid_order():
    df = _build_patient_df([[10] * 9])
    with pytest.raises(ValueError, match="Invalid order 'sideways'.*"):
        PatientDashboard().fetch_patient_phone(df, "sideways")


def test_fetch_patient_phone_missing_required_column():
    df = _build_patient_df([[10] * 9])
    df = df.drop(columns=["phone"])
    with pytest.raises(ValueError, match="missing required columns: phone"):
        PatientDashboard().fetch_patient_phone(df, "top_10")


def test_fetch_patient_phone_adds_expense_when_missing():
    expenses = [
        [1, 1, 1, 1, 1, 1, 1, 1, 10],
        [2, 2, 2, 2, 2, 2, 2, 2, 20],
    ]
    df = _build_patient_df(expenses)
    result = PatientDashboard().fetch_patient_phone(df, "top_10")
    expected_totals = [sum(row) for row in expenses][::-1]
    assert list(result["added_amt"]) == expected_totals


def test_fetch_patient_phone_respects_existing_added_amt():
    expenses = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2, 2, 2, 2],
    ]
    df = _build_patient_df(expenses, added_amt=[1000, 1])
    result = PatientDashboard().fetch_patient_phone(df, "top_10")
    assert list(result["added_amt"]) == [1000, 1]

