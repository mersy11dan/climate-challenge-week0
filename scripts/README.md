# Scripts

This directory is for small, runnable scripts that support the project (sanity checks, one-off utilities, and automation). As the project matures, reusable logic should live in `src/` and scripts should stay thin wrappers around that logic.

## Suggested organization

- Keep scripts focused on a single purpose (one script, one job).
- Prefer calling functions from `src/` rather than duplicating logic.

Example names:

- `smoke_check.py`
- `validate_environment.py`
- `run_dashboard.py` (later, if needed)

## Guidelines

- Scripts should be deterministic and avoid hidden state.
- Do not read from or write to committed data paths. Use `data/` (ignored) for local datasets.

