from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def monthly_aggregations(df: pd.DataFrame) -> pd.DataFrame:
    if "Month" not in df.columns:
        raise KeyError("Expected Month column.")
    out = (
        df.groupby("Month", as_index=False)
        .agg(
            T2M_mean=("T2M", "mean"),
            PRECTOTCORR_sum=("PRECTOTCORR", "sum"),
        )
        .sort_values("Month")
    )
    return out


def extreme_heat_days(df: pd.DataFrame, threshold_c: float = 35.0) -> pd.DataFrame:
    if "T2M_MAX" not in df.columns:
        raise KeyError("Expected T2M_MAX column.")
    out = (
        df.assign(Year=df["DATE"].dt.year)
        .groupby(["Country", "Year"], as_index=False)
        .apply(lambda g: (g["T2M_MAX"] > threshold_c).sum())
        .rename(columns={None: "ExtremeHeatDays"})
    )
    return out


def dry_days(df: pd.DataFrame, threshold_mm: float = 1.0) -> pd.DataFrame:
    if "PRECTOTCORR" not in df.columns:
        raise KeyError("Expected PRECTOTCORR column.")
    out = (
        df.assign(Year=df["DATE"].dt.year)
        .groupby(["Country", "Year"], as_index=False)
        .apply(lambda g: (g["PRECTOTCORR"] < threshold_mm).sum())
        .rename(columns={None: "DryDays"})
    )
    return out


def summary_stats_table(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    g = df.groupby("Country")[value_col]
    out = pd.DataFrame(
        {
            "mean": g.mean(),
            "median": g.median(),
            "std": g.std(),
        }
    ).reset_index()
    return out


def anova_or_kruskal_t2m(df: pd.DataFrame) -> tuple[str, float]:
    groups = []
    labels = []
    for c, g in df.groupby("Country"):
        s = g["T2M"].dropna().astype(float)
        if len(s) > 3:
            labels.append(c)
            groups.append(s.values)

    if len(groups) < 2:
        return ("insufficient_groups", float("nan"))

    # Simple normality heuristic: if any group fails Shapiro at 0.05, use Kruskal.
    shapiro_pvals = []
    for arr in groups:
        if len(arr) > 5000:
            arr = np.random.default_rng(0).choice(arr, size=5000, replace=False)
        try:
            shapiro_pvals.append(stats.shapiro(arr).pvalue)
        except Exception:
            shapiro_pvals.append(0.0)

    if any(p < 0.05 for p in shapiro_pvals):
        res = stats.kruskal(*groups)
        return ("kruskal", float(res.pvalue))

    res = stats.f_oneway(*groups)
    return ("anova", float(res.pvalue))


def vulnerability_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    A transparent, analysis-backed composite ranking:
      - Warming: slope of monthly mean T2M across months (simple linear trend)
      - Precip instability: coefficient of variation of PRECTOTCORR (std/mean)
      - Extremes: extreme heat days and dry days per year (mean across years)
    Higher composite = more vulnerable (as a heuristic for Week 0 narrative).
    """
    df = df.copy()
    df["Year"] = df["DATE"].dt.year

    # Warming proxy: within-year monthly mean then slope across months, averaged across years
    monthly = df.groupby(["Country", "Year", "Month"], as_index=False)["T2M"].mean()
    slopes = []
    for (country, year), g in monthly.groupby(["Country", "Year"]):
        g = g.dropna()
        if len(g) < 3:
            continue
        x = g["Month"].values.astype(float)
        y = g["T2M"].values.astype(float)
        slope = np.polyfit(x, y, deg=1)[0]
        slopes.append((country, slope))
    warming = (
        pd.DataFrame(slopes, columns=["Country", "warming_slope"])
        .groupby("Country", as_index=False)["warming_slope"]
        .mean()
    )

    # Precip instability
    precip = df.groupby("Country")["PRECTOTCORR"]
    precip_instab = (
        pd.DataFrame(
            {
                "Country": precip.mean().index,
                "precip_mean": precip.mean().values,
                "precip_std": precip.std().values,
            }
        )
        .assign(precip_cv=lambda d: d["precip_std"] / d["precip_mean"].replace(0, np.nan))
        .drop(columns=["precip_mean", "precip_std"])
    )

    # Extremes
    heat = (
        df.groupby(["Country", "Year"], as_index=False)
        .agg(ExtremeHeatDays=("T2M_MAX", lambda s: (s > 35).sum()))
        .groupby("Country", as_index=False)["ExtremeHeatDays"]
        .mean()
    )
    dry = (
        df.groupby(["Country", "Year"], as_index=False)
        .agg(DryDays=("PRECTOTCORR", lambda s: (s < 1).sum()))
        .groupby("Country", as_index=False)["DryDays"]
        .mean()
    )

    out = warming.merge(precip_instab, on="Country", how="outer").merge(heat, on="Country", how="outer").merge(dry, on="Country", how="outer")
    for col in ["warming_slope", "precip_cv", "ExtremeHeatDays", "DryDays"]:
        out[col] = out[col].astype(float)
        # normalize to 0..1
        mn, mx = out[col].min(), out[col].max()
        out[f"{col}_norm"] = (out[col] - mn) / (mx - mn) if mx != mn else 0.0

    out["vulnerability_score"] = (
        out["warming_slope_norm"]
        + out["precip_cv_norm"]
        + out["ExtremeHeatDays_norm"]
        + out["DryDays_norm"]
    )
    out = out.sort_values("vulnerability_score", ascending=False).reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out[
        [
            "rank",
            "Country",
            "vulnerability_score",
            "warming_slope",
            "precip_cv",
            "ExtremeHeatDays",
            "DryDays",
        ]
    ]

