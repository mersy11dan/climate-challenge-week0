from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .constants import WEATHER_VARS


@dataclass(frozen=True)
class MissingnessReport:
    counts: pd.Series
    percentages: pd.Series
    over_5pct: list[str]


@dataclass(frozen=True)
class OutlierReport:
    zscores: pd.DataFrame
    flagged_any: pd.Series
    flagged_counts: pd.Series


def add_country_column(df: pd.DataFrame, country: str) -> pd.DataFrame:
    out = df.copy()
    out["Country"] = country
    return out


def add_datetime_and_month(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "YEAR" not in out.columns or "DOY" not in out.columns:
        raise KeyError("Expected columns YEAR and DOY to create DATE.")
    out["DATE"] = pd.to_datetime(out["YEAR"] * 1000 + out["DOY"], format="%Y%j", errors="coerce")
    out["Month"] = out["DATE"].dt.month
    return out


def replace_sentinel_missing(df: pd.DataFrame, sentinel: float | int = -999) -> pd.DataFrame:
    out = df.copy()
    return out.replace(sentinel, np.nan)


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    out = df.drop_duplicates().copy()
    return out, before - len(out)


def numeric_describe(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=[np.number])
    return num.describe().T


def missingness_report(df: pd.DataFrame) -> MissingnessReport:
    counts = df.isna().sum().sort_values(ascending=False)
    percentages = (counts / len(df) * 100).round(2)
    over_5pct = percentages[percentages > 5].index.tolist()
    return MissingnessReport(counts=counts, percentages=percentages, over_5pct=over_5pct)


def compute_zscores(df: pd.DataFrame, cols: list[str] | None = None) -> OutlierReport:
    cols = cols or WEATHER_VARS
    existing = [c for c in cols if c in df.columns]
    z = pd.DataFrame(index=df.index)
    for c in existing:
        # nan_policy ensures missing values don't contaminate z-score.
        z[c] = stats.zscore(df[c].astype(float), nan_policy="omit")
    flagged_any = (z.abs() > 3).any(axis=1) if len(existing) else pd.Series(False, index=df.index)
    flagged_counts = (z.abs() > 3).sum(axis=0).sort_values(ascending=False)
    return OutlierReport(zscores=z, flagged_any=flagged_any, flagged_counts=flagged_counts)


def add_temperature_range(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "T2M_MAX" in out.columns and "T2M_MIN" in out.columns:
        out["T2M_RANGE"] = out["T2M_MAX"] - out["T2M_MIN"]
    return out


def drop_rows_over_missingness(df: pd.DataFrame, threshold_pct: float = 30.0) -> tuple[pd.DataFrame, int]:
    row_pct_missing = df.isna().mean(axis=1) * 100
    mask = row_pct_missing <= threshold_pct
    dropped = int((~mask).sum())
    return df.loc[mask].copy(), dropped


def forward_fill_weather_vars(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    cols = cols or WEATHER_VARS
    existing = [c for c in cols if c in df.columns]
    out = df.copy()
    if "DATE" in out.columns:
        out = out.sort_values("DATE")
    if existing:
        out[existing] = out[existing].ffill()
    return out


def cap_outliers_iqr(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            continue
        s = out[c].astype(float)
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lo = q1 - 1.5 * iqr
        hi = q3 + 1.5 * iqr
        out[c] = s.clip(lower=lo, upper=hi)
    return out


def clean_country_dataframe(
    raw_df: pd.DataFrame,
    country: str,
    *,
    outlier_strategy: str = "cap",
) -> tuple[pd.DataFrame, dict]:
    """
    Returns (clean_df, info) where info holds key counts for reporting in notebooks.

    outlier_strategy:
      - "cap": cap selected weather variables using IQR clipping (retains days, reduces leverage)
      - "retain": keep as-is
      - "drop": drop any row flagged by abs(z) > 3 on selected weather variables
    """
    info: dict[str, object] = {}

    df = add_country_column(raw_df, country=country)
    df = add_datetime_and_month(df)
    df = replace_sentinel_missing(df, sentinel=-999)

    df, dupes_removed = remove_duplicates(df)
    info["duplicates_removed"] = dupes_removed

    df = add_temperature_range(df)

    outliers = compute_zscores(df)
    info["outlier_flagged_rows"] = int(outliers.flagged_any.sum())
    info["outlier_flagged_by_col"] = outliers.flagged_counts.to_dict()

    if outlier_strategy == "drop":
        before = len(df)
        df = df.loc[~outliers.flagged_any].copy()
        info["outlier_rows_dropped"] = before - len(df)
    elif outlier_strategy == "cap":
        df = cap_outliers_iqr(df, cols=[c for c in WEATHER_VARS if c in df.columns])
        info["outlier_rows_dropped"] = 0
    elif outlier_strategy == "retain":
        info["outlier_rows_dropped"] = 0
    else:
        raise ValueError("outlier_strategy must be one of: cap, retain, drop")

    df, dropped_missing = drop_rows_over_missingness(df, threshold_pct=30.0)
    info["rows_dropped_over_30pct_missing"] = dropped_missing

    df = forward_fill_weather_vars(df)

    # Final: ensure DATE is datetime and Month is derived from it.
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df["Month"] = df["DATE"].dt.month
    return df, info

