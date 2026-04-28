from __future__ import annotations

from pathlib import Path

import pandas as pd

from .paths import paths


def raw_csv_path(country: str, data_dir: Path | None = None) -> Path:
    d = data_dir or paths().data_dir
    return d / f"{country.lower()}.csv"


def cleaned_csv_path(country: str, data_dir: Path | None = None) -> Path:
    d = data_dir or paths().data_dir
    return d / f"{country.lower()}_clean.csv"


def load_raw_country_csv(country: str, data_dir: Path | None = None) -> pd.DataFrame:
    p = raw_csv_path(country=country, data_dir=data_dir)
    if not p.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at {p}. Place it under data/ as data/{country.lower()}.csv"
        )
    return pd.read_csv(p)


def save_cleaned_country_csv(df: pd.DataFrame, country: str, data_dir: Path | None = None) -> Path:
    p = cleaned_csv_path(country=country, data_dir=data_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return p


def load_cleaned_country_csv(country: str, data_dir: Path | None = None) -> pd.DataFrame:
    p = cleaned_csv_path(country=country, data_dir=data_dir)
    if not p.exists():
        raise FileNotFoundError(
            f"Cleaned CSV not found at {p}. Run the Task 2 notebook for {country} first."
        )
    return pd.read_csv(p, parse_dates=["DATE"])

