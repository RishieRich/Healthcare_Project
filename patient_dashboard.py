from typing import Optional, Sequence

import pandas as pd

class PatientDashboard:
    """Dashboard utilities for patient discharge information."""

    def read_csv(self, path: str) -> pd.DataFrame:
        """Read a CSV file with comma delimiter and return a DataFrame."""
        return pd.read_csv(path, header=0, delimiter=',')

    def add_total_expense_column(
        self,
        patient_discharge_df: pd.DataFrame,
        expense_columns: Optional[Sequence[str]] = None,
        expense_prefix: Optional[str] = "expense_",
    ) -> pd.DataFrame:
        """Append 'added_amt' column with the sum of expenses for each patient.

        The expense columns can be supplied explicitly through ``expense_columns`` or
        inferred by matching the provided ``expense_prefix`` (``"expense_"`` by
        default). All referenced columns must exist otherwise a ``ValueError`` is
        raised. Values are coerced to numeric to ensure non-numeric entries do not
        cause runtime errors during aggregation.
        """

        df = patient_discharge_df

        if expense_columns:
            missing_columns = [col for col in expense_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(
                    "Missing required expense columns: " + ", ".join(missing_columns)
                )
            expense_fields = expense_columns
        else:
            if not expense_prefix:
                raise ValueError(
                    "Either expense_columns must be provided or a valid expense_prefix must be set."
                )
            expense_fields = [col for col in df.columns if col.startswith(expense_prefix)]
            if not expense_fields:
                raise ValueError(
                    f"No expense columns found with prefix '{expense_prefix}'."
                )

        expense_values = df[expense_fields].apply(pd.to_numeric, errors="coerce").fillna(0)
        df["added_amt"] = expense_values.sum(axis=1)
        return df

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
