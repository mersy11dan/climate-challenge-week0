# Notebooks

This directory is for exploratory and reporting notebooks (EDA, experiments, quick visual checks). Keep notebooks focused and reproducible: if code becomes reusable, move it into `src/` and import it from notebooks.

## Naming convention

Use a consistent, sortable naming scheme:

- `task1_01_project_setup.ipynb`
- `task2_01_eda_overview.ipynb`
- `task2_02_data_quality_checks.ipynb`
- `task3_01_model_baseline.ipynb`

General format:

`task<taskNumber>_<twoDigitOrder>_<short_description>.ipynb`

## Tips

- Prefer relative paths and config variables over hard-coded absolute paths.
- Do not store datasets in this repository. Put files under `data/` (ignored) and document how to obtain them.

