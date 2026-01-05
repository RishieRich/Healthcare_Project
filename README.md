# Healthcare Analysis

A small toolkit for exploring hospital discharge data and building KPI-focused dashboards. The repository currently centers on pandas-based transformations with supporting notebooks for department-level, patient-level, and “powerplay” dashboards.

## Repository structure

- `patient_dashboard.py` — core data utilities used across the dashboards.
- `patient_dashboard.ipynb`, `department_wise_dashboard.ipynb`, `powerplay_wise_dahboard.ipynb`, `outpatient_details_script.ipynb`, `patient_discharge_details_script.ipynb`, `patient_wise_dashboard.ipynb` — exploratory notebooks for specific KPIs and reporting slices.
- `tests/` — pytest coverage for the `PatientDashboard` helper.
- `requirements.txt` — minimal runtime and test dependencies.

## Getting started

1. Create a Python 3.10+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the unit tests to confirm the environment:
   ```bash
   pytest
   ```
4. Open the notebooks in your preferred environment (Jupyter, VS Code, or similar) to explore or extend the dashboards.

## Core helper usage

`patient_dashboard.py` exposes a `PatientDashboard` class with a few focused utilities:

- **Reading data**: `read_csv(path)` loads comma-delimited CSV files into DataFrames.
- **Expense aggregation**: `add_total_expense_column(df, expense_columns=None, expense_prefix="expense_")` sums numeric expense columns and adds an `added_amt` column. The method validates expected columns and safely coerces non-numeric entries.
- **Patient rankings**: `fetch_patient_phone(df, order)` returns the top or bottom 10 patients by `added_amt`, including phone and department context.
- **Age-enriched details**: `fetch_patient_by_age(discharge_df, details_df)` joins age information from a patient-details table, then sorts by age to highlight senior patients with their location and total spend.
- **Exporting**: `to_csv(df, path)` persists transformed data.

## Current strengths (quick code review)

- **Strict column validation**: Expense aggregation explicitly checks for missing columns and clear error messaging.
- **Defensive numeric handling**: Non-numeric expense values are coerced with `errors="coerce"` to avoid runtime failures.
- **Focused tests**: Pytest covers prefix-based expense aggregation and missing-column errors.

## Improvement opportunities

- **Avoid in-place mutation**: Several helpers mutate incoming DataFrames (e.g., adding `added_amt` and `age`). Returning copies or documenting mutation would reduce side effects when functions are reused.
- **Type hints and contracts**: Expanding type hints (e.g., accepted `order` values) and adding docstring examples would clarify expected inputs.
- **Data validation**: Schema validation (pydantic models or pandera checks) would ensure dashboard inputs are well-formed before aggregation.
- **Packaging**: Converting the utilities into a small package/CLI with entry points for batch runs would improve reproducibility beyond notebooks.
- **Notebook hygiene**: Adding lightweight smoke tests that load each notebook’s key cells (via `nbmake` or `papermill`) would guard against regression in dashboard logic.

## Suggested roadmap

1. **Data contract & validation**
   - Define a minimal schema for discharge and patient detail tables (required columns, types, nullability).
   - Introduce validation with pandera or pydantic to fail fast before computations.
2. **API hardening**
   - Make helper methods return copies by default and document mutating behavior.
   - Add error handling for missing/duplicate patient identifiers when merging age and expense data.
3. **Automation & testing**
   - Expand pytest coverage to include `fetch_patient_phone`, `fetch_patient_by_age`, and `to_csv`.
   - Add notebook execution checks (e.g., `pytest --nbmake`) to ensure dashboards run end-to-end.
4. **Packaging & distribution**
   - Convert `patient_dashboard.py` into an installable package with a CLI (e.g., `healthcare-dashboard build --input discharge.csv`).
   - Provide sample datasets and expected outputs to accelerate onboarding.
5. **Documentation**
   - Document expected input CSV headers and sample records.
   - Add how-to guides for generating department/patient/powerplay dashboard extracts.

## Contributors :sparkles:
- [Rishikesh R Pote](https://github.com/RishikeshPote)
- [Amrut Kinage](https://github.com/amrutkinage)
- [Quaid Johar](https://github.com/Equinox-13)
