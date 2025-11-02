import pandas as pd

class PatientDashboard:
    """Dashboard utilities for patient discharge information."""

    def read_csv(self, path: str) -> pd.DataFrame:
        """Read a CSV file with comma delimiter and return a DataFrame."""
        return pd.read_csv(path, header=0, delimiter=',')

    def add_total_expense_column(self, patient_discharge_df: pd.DataFrame) -> pd.DataFrame:
        """Append 'added_amt' column with the sum of expenses for each patient."""
        patient_discharge_df['added_amt'] = patient_discharge_df.iloc[:, 11:20].sum(axis=1)
        return patient_discharge_df

    def fetch_patient_phone(self, patient_discharge_df: pd.DataFrame, order: str) -> pd.DataFrame:
        """Return top or bottom 10 patients based on 'added_amt'."""
        required_columns = {"registrationno", "patientname", "phone", "department"}
        missing_columns = required_columns.difference(patient_discharge_df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"patient_discharge_df is missing required columns: {missing}"
            )

        if "added_amt" not in patient_discharge_df.columns:
            patient_discharge_df = self.add_total_expense_column(patient_discharge_df)

        normalized_order = order.lower()
        if normalized_order == "top_10":
            subset = patient_discharge_df.nlargest(10, ["added_amt"])
        elif normalized_order == "bottom_10":
            subset = patient_discharge_df.nsmallest(10, ["added_amt"])
        else:
            raise ValueError(
                f"Invalid order '{order}'. Expected 'top_10' or 'bottom_10'."
            )
        return subset[["registrationno", "patientname", "phone", "department", "added_amt"]]

    def fetch_patient_by_age(self, patient_discharge_df: pd.DataFrame, patient_details_df: pd.DataFrame) -> pd.DataFrame:
        """Return patient details sorted by maximum age."""
        patient_discharge_df['age'] = patient_discharge_df.registrationno.map(
            patient_details_df.set_index("registrationno")['age']
        )
        cols = [
            "registrationno",
            "phone",
            "patientname",
            "age",
            "cityname",
            "districtname",
            "statename",
            "added_amt",
        ]
        patient_discharge_max_age_df = patient_discharge_df[cols]
        return patient_discharge_max_age_df.sort_values(by=['age'], ascending=False)

    def to_csv(self, df: pd.DataFrame, path: str) -> bool:
        """Write the given DataFrame to CSV and return True."""
        df.to_csv(path, encoding='utf-8', index=False)
        return True
