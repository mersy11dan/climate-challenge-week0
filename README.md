# Climate Challenge — Week 0 Starter

A clean, submission-ready scaffold for the **10 Academy Climate Challenge**. This Week 0 repo focuses on environment setup, reproducible structure, and CI hygiene so you can move into Task 2 (EDA) and Task 3 (dashboard/modeling) without rework.

## Project structure

```
climate-challenge-week0/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .vscode/
│   └── settings.json
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── scripts/
│   ├── __init__.py
│   └── README.md
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── .gitignore
├── README.md
├── requirements.txt
└── interim_report.md
```

## Clone the repository

```powershell
git clone <YOUR_REPO_URL>
cd climate-challenge-week0
```

## Create and activate a virtual environment (Windows PowerShell)

Create a `.venv`:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, you can enable script execution for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the notebooks

1. Place the raw CSV files in `data/` (these are ignored by Git):

- `data/ethiopia.csv`
- `data/kenya.csv`
- `data/sudan.csv`
- `data/tanzania.csv`
- `data/nigeria.csv`

2. Start Jupyter:

```powershell
jupyter notebook
```

3. Open and run the notebooks in `notebooks/` (Task 2 EDA and Task 3 comparison).

## Quick local “CI in spirit” checks

These checks mirror what the GitHub Actions workflow verifies.

```powershell
python --version
python -c "import pandas as pd; import numpy as np; print('pandas', pd.__version__); print('numpy', np.__version__)"
pytest -q
```

## Run the dashboard (optional)

The Streamlit app reads the cleaned CSV outputs (created by the Task 2 notebooks) from `data/`:

```powershell
streamlit run app/main.py
```

## Keep data out of GitHub

This repository is intentionally **code-only**:

- Put datasets under `data/` (ignored by Git).
- Never commit CSVs: `*.csv` is ignored by default.
- If you must share a dataset location, document it in text (e.g., a download link) instead of committing files.

See `.gitignore` for the enforced rules.

## What’s next (Tasks 2 and 3)

- **Task 2** will add EDA notebooks and reusable preprocessing utilities under `src/`.
- **Task 3** will add a dashboard (likely `streamlit`) and any modeling/experimentation code with tests where appropriate.

