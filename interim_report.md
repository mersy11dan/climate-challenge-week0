# Interim Report — 10 Academy Climate Challenge (Week 0)

## Task 1 summary

Task 1 focused on establishing a clean project scaffold, reproducible environment setup, and basic CI checks to ensure the repository is ready for subsequent analysis work.

## What has been completed so far

- Created a standard repository structure for notebooks, scripts, source code, and tests.
- Added a `.gitignore` that prevents committing datasets (`data/`) and all CSV files.
- Added `requirements.txt` with core libraries needed for EDA and future dashboard work.
- Prepared minimal VS Code workspace settings to keep the project tidy and Python-friendly.
- Added a simple GitHub Actions workflow to validate Python setup and dependency installation.
- Wrote baseline documentation describing how to set up the environment and how work will be organized.

## Tools and environment setup

- **Language**: Python
- **Environment**: Virtual environment (`.venv`) on Windows PowerShell
- **Core libraries**: pandas, numpy, matplotlib, seaborn, scipy, scikit-learn
- **Notebooks**: Jupyter / Notebook
- **Dashboard (future)**: Streamlit
- **Testing**: pytest
- **CI**: GitHub Actions (install + smoke imports)

## Git workflow used

- Local development using feature branches.
- Frequent small commits with clear intent.
- Pull requests (when collaborating) to keep changes reviewable and traceable.

## Branching and commit strategy

- Default branch: `main`
- Branch naming (examples):
  - `chore/scaffold-week0`
  - `docs/update-readme`
  - `ci/add-python-smoke-check`
- Commit style: Conventional Commits (examples):
  - `chore: add week0 project scaffold`
  - `docs: add interim report draft`
  - `ci: add github actions python smoke check`

## Task 2 approach outline

Task 2 will focus on exploratory data analysis and preparing reusable utilities:

- Acquire the dataset externally and store locally under `data/` (ignored by Git).
- Create EDA notebooks under `notebooks/` using the naming convention described there.
- Implement reusable functions under `src/` (e.g., loading, cleaning, validation, feature engineering).
- Add lightweight tests in `tests/` for critical utilities (e.g., schema checks, missing value handling).
- Maintain reproducibility by documenting dataset sources and any required setup steps.

## Next steps

- Initialize the Git repository inside the project folder and push to GitHub.
- Confirm CI passes on the default branch.
- Begin Task 2 by adding the first EDA notebook(s) and initial data quality checks.
- Expand `src/` with reusable preprocessing utilities as patterns emerge from EDA.


