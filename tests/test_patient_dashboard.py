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


def _build_discharge_df():
    return pd.DataFrame(
        {
            "registrationno": [101, 102, 103],
            "phone": ["123", "456", "789"],
            "patientname": ["Alice", "Bob", "Charlie"],
            "cityname": ["CityA", "CityB", "CityC"],
            "districtname": ["DistrictA", "DistrictB", "DistrictC"],
            "statename": ["StateA", "StateB", "StateC"],
            "added_amt": [1000, 500, 1500],
        }
    )


def _build_details_df(ages):
    return pd.DataFrame(
        {
            "registrationno": [101, 102, 103],
            "age": ages,
        }
    )


def test_fetch_patient_by_age_success():
    discharge_df = _build_discharge_df()
    details_df = _build_details_df([65, 70, 55])

    result = PatientDashboard().fetch_patient_by_age(discharge_df, details_df)

    # Ensure original dataframe is untouched
    assert "age" not in discharge_df.columns

    # Expect rows sorted by age descending
    expected_order = [102, 101, 103]
    assert list(result["registrationno"]) == expected_order


def test_fetch_patient_by_age_drops_missing_age():
    discharge_df = _build_discharge_df()
    details_df = _build_details_df([65, None, 55])

    result = PatientDashboard().fetch_patient_by_age(discharge_df, details_df)

    # Registration with missing age should be dropped
    assert list(result["registrationno"]) == [101, 103]


def test_fetch_patient_by_age_unmatched_registration():
    discharge_df = _build_discharge_df()
    details_df = pd.DataFrame(
        {
            "registrationno": [101, 104, 105],
            "age": [65, 70, 55],
        }
    )

    with pytest.raises(ValueError) as exc:
        PatientDashboard().fetch_patient_by_age(discharge_df, details_df)

    assert "Registration numbers not found" in str(exc.value)

