import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from patient_dashboard import PatientDashboard


def _make_patient_discharge_df(rows):
    """Utility to create discharge data with expense columns."""
    base_columns = [
        "registrationno",
        "patientname",
        "phone",
        "department",
        "dummy0",
        "dummy1",
        "dummy2",
        "dummy3",
        "dummy4",
        "dummy5",
        "dummy6",
    ]
    expense_columns = [f"expense{i}" for i in range(9)]
    other_columns = [
        "cityname",
        "districtname",
        "statename",
    ]
    columns = base_columns + expense_columns + other_columns
    return pd.DataFrame(rows, columns=columns)


def test_read_csv_success(tmp_path):
    dashboard = PatientDashboard()
    df = pd.DataFrame({"registrationno": [1, 2], "patientname": ["Alice", "Bob"]})
    csv_path = tmp_path / "patients.csv"
    df.to_csv(csv_path, index=False)

    result = dashboard.read_csv(csv_path)

    pd.testing.assert_frame_equal(result, df)


def test_read_csv_missing_file():
    dashboard = PatientDashboard()
    with pytest.raises(FileNotFoundError):
        dashboard.read_csv("non_existent_file.csv")


def test_add_total_expense_column():
    data = [
        [1, "Alice", "555", "cardiology", *(["d"] * 7), *range(1, 10), "City", "District", "State"],
        [2, "Bob", "777", "oncology", *(["d"] * 7), *range(2, 11), "City", "District", "State"],
    ]
    df = _make_patient_discharge_df(data)

    result = PatientDashboard().add_total_expense_column(df.copy())

    assert list(result['added_amt']) == [45, 54]


def test_fetch_patient_phone_top_and_bottom():
    dashboard = PatientDashboard()
    rows = []
    for i in range(1, 16):
        expenses = list(range(i, i + 9))
        rows.append([i, f"Patient {i}", f"555{i:03d}", "dept", *(["d"] * 7), *expenses, "City", "District", "State"])
    discharge_df = _make_patient_discharge_df(rows)
    discharge_df = dashboard.add_total_expense_column(discharge_df)

    top = dashboard.fetch_patient_phone(discharge_df, "top_10")
    bottom = dashboard.fetch_patient_phone(discharge_df, "bottom_10")

    assert top['added_amt'].is_monotonic_decreasing
    assert bottom['added_amt'].is_monotonic_increasing
    assert len(top) == len(bottom) == 10


def test_fetch_patient_phone_invalid_order():
    dashboard = PatientDashboard()
    df = pd.DataFrame({"registrationno": [], "added_amt": []})

    with pytest.raises(ValueError, match="order must be 'top_10' or 'bottom_10'"):
        dashboard.fetch_patient_phone(df, "median")


def test_fetch_patient_by_age_sorted_with_missing_age():
    dashboard = PatientDashboard()
    discharge_rows = [
        [1, "Alice", "555", "cardiology", *(["d"] * 7), *range(1, 10), "CityA", "DistrictA", "StateA"],
        [2, "Bob", "777", "oncology", *(["d"] * 7), *range(2, 11), "CityB", "DistrictB", "StateB"],
        [3, "Carol", "888", "ortho", *(["d"] * 7), *range(3, 12), "CityC", "DistrictC", "StateC"],
    ]
    discharge_df = dashboard.add_total_expense_column(_make_patient_discharge_df(discharge_rows))
    patient_details_df = pd.DataFrame(
        {
            "registrationno": [1, 2],
            "age": [65, 72],
        }
    )

    result = dashboard.fetch_patient_by_age(discharge_df, patient_details_df)

    assert list(result['registrationno'])[:2] == [2, 1]
    assert pd.isna(result.iloc[-1]['age'])


def test_to_csv_success(tmp_path):
    dashboard = PatientDashboard()
    df = pd.DataFrame({"registrationno": [1], "patientname": ["Alice"]})
    csv_path = tmp_path / "output.csv"

    assert dashboard.to_csv(df, csv_path) is True
    saved = pd.read_csv(csv_path)
    pd.testing.assert_frame_equal(saved, df)


def test_to_csv_failure_when_directory_missing(tmp_path):
    dashboard = PatientDashboard()
    df = pd.DataFrame({"registrationno": [1]})
    missing_dir_path = tmp_path / "missing" / "output.csv"

    with pytest.raises(OSError):
        dashboard.to_csv(df, missing_dir_path)

