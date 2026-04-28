from __future__ import annotations

from pathlib import Path
import sys

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.constants import COUNTRIES
from src.paths import paths


def md_cell(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code_cell(code: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(code)


EDA_INTRO = """# Task 2 — EDA ({country_title})

This notebook performs a clean, reproducible EDA workflow for **{country_title}** using the raw file:

- `data/{country}.csv`

It produces a cleaned dataset saved locally (and ignored by Git):

- `data/{country}_clean.csv`

The workflow follows the Week 0 requirements:

- Add `Country`
- Convert `YEAR` + `DOY` → `DATE` via `pd.to_datetime(df["YEAR"] * 1000 + df["DOY"], format="%Y%j")`
- Extract `Month`
- Replace sentinel `-999` with `NaN`
- Remove duplicate rows
- Missingness report (counts/percentages; flag >5%)
- Z-score outlier flagging for core weather variables; decide an outlier strategy and justify
- Handle remaining missingness (drop rows >30% missing; forward-fill weather variables)
- Save cleaned output and generate required charts with interpretations
"""


EDA_CODE = """\
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cleaning import (
    clean_country_dataframe,
    missingness_report,
    numeric_describe,
    compute_zscores,
)
from src.io import load_raw_country_csv, save_cleaned_country_csv

sns.set_theme(style="whitegrid")

COUNTRY = "{country}"
"""


EDA_LOAD_AND_QC = """\
df_raw = load_raw_country_csv(COUNTRY)
df_raw.head()
"""


EDA_CLEAN = """\
# We choose outlier_strategy="cap" to avoid removing real extreme-weather days.
# Capping reduces undue leverage on correlations/summary stats while preserving
# seasonality and rare-event frequency (important for climate risk narratives).

df, info = clean_country_dataframe(df_raw, COUNTRY, outlier_strategy="cap")
info
"""


EDA_REPORTS = """\
desc = numeric_describe(df)
desc
"""


EDA_MISSING = """\
miss = missingness_report(df)
pd.DataFrame({"missing_count": miss.counts, "missing_pct": miss.percentages}).head(20)
"""


EDA_MISSING_MD = """\
## Missingness interpretation

The table above lists missing counts and percentages by column (top 20). Columns with **> 5%** missing are flagged for attention.

In climate time series, small gaps are common (sensor/collection issues). We handle remaining gaps by:

- **Dropping** rows with more than **30%** missing values (likely low-quality days)
- **Forward-filling** core weather variables (reasonable for short gaps in daily data)
"""


EDA_OUTLIERS = """\
out = compute_zscores(df)
out.flagged_counts.head(10)
"""


EDA_OUTLIERS_MD = """\
## Outliers decision

We flagged outliers using **z-scores** on core variables (abs(z) > 3). Instead of dropping these rows, we **cap** weather-variable outliers using an IQR-based clip.

**Why cap?**

- Climate extremes are often *real* and policy-relevant (heat waves, heavy rainfall).
- Dropping them can bias extreme-day counts and understate vulnerability.
- Capping prevents a small number of values from dominating correlations and summary statistics.
"""


EDA_SAVE = """\
out_path = save_cleaned_country_csv(df, COUNTRY)
out_path
"""


EDA_CHARTS = """\
monthly = (
    df.groupby("Month", as_index=False)
    .agg(T2M_mean=("T2M", "mean"), PRECTOTCORR_sum=("PRECTOTCORR", "sum"))
    .sort_values("Month")
)

# 1) Monthly average T2M line chart + warmest/coolest annotation
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly["Month"], monthly["T2M_mean"], marker="o")
ax.set_title(f"{COUNTRY.title()} — Monthly Average Temperature (T2M)")
ax.set_xlabel("Month")
ax.set_ylabel("T2M (°C)")

warm = monthly.loc[monthly["T2M_mean"].idxmax()]
cool = monthly.loc[monthly["T2M_mean"].idxmin()]
ax.annotate(f"Warmest: M{int(warm['Month'])}", (warm["Month"], warm["T2M_mean"]),
            textcoords="offset points", xytext=(10, 10))
ax.annotate(f"Coolest: M{int(cool['Month'])}", (cool["Month"], cool["T2M_mean"]),
            textcoords="offset points", xytext=(10, -15))
plt.show()
"""


EDA_CHARTS_MD_1 = """\
## Interpretation (Monthly temperature)

The line chart shows the seasonal temperature cycle. The annotated warmest/coolest months highlight the strongest seasonal contrast, useful for discussing exposure to heat stress and the timing of hottest periods.
"""


EDA_CHARTS_2 = """\
# 2) Monthly total precipitation bar chart + peak rainy season annotation
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(monthly["Month"], monthly["PRECTOTCORR_sum"])
ax.set_title(f"{COUNTRY.title()} — Monthly Total Precipitation (PRECTOTCORR)")
ax.set_xlabel("Month")
ax.set_ylabel("Total PRECTOTCORR (mm)")

peak = monthly.loc[monthly["PRECTOTCORR_sum"].idxmax()]
ax.annotate(f"Peak rains: M{int(peak['Month'])}",
            (peak["Month"], peak["PRECTOTCORR_sum"]),
            textcoords="offset points", xytext=(10, 10))
plt.show()
"""


EDA_CHARTS_MD_2 = """\
## Interpretation (Monthly precipitation)

The precipitation bar chart highlights the seasonality of rainfall and the peak rainy month. This is a simple way to identify the main wet season and discuss potential flood risk vs. dry-season water stress.
"""


EDA_CHARTS_3 = """\
# 3) Correlation heatmap (numeric)
num = df.select_dtypes(include=[np.number]).copy()
corr = num.corr(numeric_only=True)
plt.figure(figsize=(10, 7))
sns.heatmap(corr, cmap="coolwarm", center=0)
plt.title(f"{COUNTRY.title()} — Correlation Heatmap (Numeric Features)")
plt.show()
"""


EDA_CHARTS_MD_3 = """\
## Interpretation (Correlation)

Correlations show which variables move together (e.g., temperature relationships across max/min, or wind components). Strong relationships can suggest shared drivers or measurement coupling, but correlation does not imply causation.
"""


EDA_CHARTS_4 = """\
# 4) Scatter: T2M vs RH2M
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x="T2M", y="RH2M", alpha=0.35)
plt.title(f"{COUNTRY.title()} — T2M vs RH2M")
plt.show()
"""


EDA_CHARTS_MD_4 = """\
## Interpretation (T2M vs RH2M)

This scatterplot helps assess how humidity changes with temperature. A negative pattern is common in some climates (warmer days often coincide with lower relative humidity), which can amplify heat stress impacts.
"""


EDA_CHARTS_5 = """\
# 5) Scatter: T2M_RANGE vs WS2M
if "T2M_RANGE" in df.columns and "WS2M" in df.columns:
    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=df, x="T2M_RANGE", y="WS2M", alpha=0.35)
    plt.title(f"{COUNTRY.title()} — T2M_RANGE vs WS2M")
    plt.show()
else:
    print("T2M_RANGE or WS2M missing; cannot plot.")
"""


EDA_CHARTS_MD_5 = """\
## Interpretation (T2M_RANGE vs WS2M)

Daily temperature range is influenced by cloud cover, moisture, and winds. This plot provides a quick diagnostic: windy regimes can reduce temperature range via mixing, while calm clear days can show larger ranges.
"""


EDA_CHARTS_6 = """\
# 6) Histogram of PRECTOTCORR
plt.figure(figsize=(7, 4))
sns.histplot(df["PRECTOTCORR"].dropna(), bins=40, kde=True)
plt.title(f"{COUNTRY.title()} — Distribution of PRECTOTCORR")
plt.xlabel("PRECTOTCORR (mm)")
plt.show()
"""


EDA_CHARTS_MD_6 = """\
## Interpretation (Precipitation distribution)

Daily precipitation is usually right-skewed: many low/zero-rain days with fewer heavy-rain days. The tail of the distribution is important for flood and extreme-rainfall narratives.
"""


EDA_CHARTS_7 = """\
# 7) Bubble chart: T2M vs RH2M with PRECTOTCORR as bubble size
plt.figure(figsize=(7, 5))
sizes = (df["PRECTOTCORR"].fillna(0).clip(0, df["PRECTOTCORR"].quantile(0.99)) + 0.1) * 10
plt.scatter(df["T2M"], df["RH2M"], s=sizes, alpha=0.25)
plt.title(f"{COUNTRY.title()} — T2M vs RH2M (bubble size = PRECTOTCORR)")
plt.xlabel("T2M (°C)")
plt.ylabel("RH2M (%)")
plt.show()
"""


EDA_CHARTS_MD_7 = """\
## Interpretation (Bubble chart)

This view combines temperature–humidity conditions with rainfall intensity. Large bubbles clustering in certain temperature/humidity ranges can indicate the atmospheric regimes associated with rainfall events.
"""


def build_country_eda_notebook(country: str) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md_cell(EDA_INTRO.format(country=country, country_title=country.title())),
        code_cell(EDA_CODE.format(country=country)),
        md_cell("## Load data"),
        code_cell(EDA_LOAD_AND_QC),
        md_cell("## Clean + feature engineering"),
        code_cell(EDA_CLEAN),
        md_cell("## Summary statistics"),
        code_cell(EDA_REPORTS),
        md_cell("## Missing values"),
        code_cell(EDA_MISSING),
        md_cell(EDA_MISSING_MD),
        md_cell("## Outliers"),
        code_cell(EDA_OUTLIERS),
        md_cell(EDA_OUTLIERS_MD),
        md_cell("## Save cleaned output"),
        code_cell(EDA_SAVE),
        md_cell("## Visualizations"),
        code_cell(EDA_CHARTS),
        md_cell(EDA_CHARTS_MD_1),
        code_cell(EDA_CHARTS_2),
        md_cell(EDA_CHARTS_MD_2),
        code_cell(EDA_CHARTS_3),
        md_cell(EDA_CHARTS_MD_3),
        code_cell(EDA_CHARTS_4),
        md_cell(EDA_CHARTS_MD_4),
        code_cell(EDA_CHARTS_5),
        md_cell(EDA_CHARTS_MD_5),
        code_cell(EDA_CHARTS_6),
        md_cell(EDA_CHARTS_MD_6),
        code_cell(EDA_CHARTS_7),
        md_cell(EDA_CHARTS_MD_7),
    ]
    return nb


def build_task3_comparison_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        md_cell(
            """# Task 3 — Cross-country comparison

This notebook loads the **cleaned** outputs from Task 2:

- `data/<country>_clean.csv` for Ethiopia, Kenya, Sudan, Tanzania, Nigeria

It then compares temperature and precipitation patterns, computes extreme heat and dry-day metrics, runs a cross-country statistical test (ANOVA/Kruskal), and produces a vulnerability ranking for COP32-style narrative.
"""
        ),
        code_cell(
            """\
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.constants import COUNTRIES
from src.io import load_cleaned_country_csv
from src.analysis import (
    summary_stats_table,
    anova_or_kruskal_t2m,
    vulnerability_ranking,
)

sns.set_theme(style="whitegrid")
"""
        ),
        md_cell("## Load and concatenate cleaned datasets"),
        code_cell(
            """\
dfs = []
for c in COUNTRIES:
    d = load_cleaned_country_csv(c)
    d["Country"] = c
    d["DATE"] = pd.to_datetime(d["DATE"], errors="coerce")
    d["Month"] = d["DATE"].dt.month
    dfs.append(d)

df_all = pd.concat(dfs, ignore_index=True)
df_all.head()
"""
        ),
        md_cell("## Monthly average T2M (all countries)"),
        code_cell(
            """\
monthly = (
    df_all.groupby(["Country", "Month"], as_index=False)["T2M"]
    .mean()
    .sort_values(["Country", "Month"])
)

plt.figure(figsize=(10, 5))
for c in COUNTRIES:
    g = monthly[monthly["Country"] == c]
    plt.plot(g["Month"], g["T2M"], marker="o", label=c.title())
plt.title("Monthly Average Temperature (T2M) — All Countries")
plt.xlabel("Month")
plt.ylabel("T2M (°C)")
plt.legend(ncol=3)
plt.show()
"""
        ),
        md_cell("## Side-by-side boxplots of precipitation (PRECTOTCORR)"),
        code_cell(
            """\
plt.figure(figsize=(10, 5))
sns.boxplot(data=df_all, x="Country", y="PRECTOTCORR")
plt.title("Daily Precipitation Distribution (PRECTOTCORR) by Country")
plt.xlabel("Country")
plt.ylabel("PRECTOTCORR (mm)")
plt.show()
"""
        ),
        md_cell("## Summary tables (T2M and PRECTOTCORR)"),
        code_cell(
            """\
summary_t2m = summary_stats_table(df_all, "T2M")
summary_prect = summary_stats_table(df_all, "PRECTOTCORR")

display(summary_t2m)
display(summary_prect)
"""
        ),
        md_cell("## Extreme heat days (T2M_MAX > 35°C) and dry days (PRECTOTCORR < 1mm)"),
        code_cell(
            """\
df_all["Year"] = df_all["DATE"].dt.year

heat = (
    df_all.groupby(["Country", "Year"], as_index=False)
    .agg(ExtremeHeatDays=("T2M_MAX", lambda s: (s > 35).sum()))
)
dry = (
    df_all.groupby(["Country", "Year"], as_index=False)
    .agg(DryDays=("PRECTOTCORR", lambda s: (s < 1).sum()))
)

display(heat.head())
display(dry.head())
"""
        ),
        md_cell("### Plot extreme heat days"),
        code_cell(
            """\
plt.figure(figsize=(11, 5))
sns.barplot(data=heat, x="Year", y="ExtremeHeatDays", hue="Country")
plt.title("Extreme Heat Days (T2M_MAX > 35°C) by Country and Year")
plt.show()
"""
        ),
        md_cell("### Plot dry days"),
        code_cell(
            """\
plt.figure(figsize=(11, 5))
sns.barplot(data=dry, x="Year", y="DryDays", hue="Country")
plt.title("Dry Days (PRECTOTCORR < 1mm) by Country and Year")
plt.show()
"""
        ),
        md_cell("## Cross-country statistical test on T2M"),
        code_cell(
            """\
test_name, p_value = anova_or_kruskal_t2m(df_all.dropna(subset=["T2M"]))
test_name, p_value
"""
        ),
        md_cell(
            """Interpretation:

- A small p-value (e.g., < 0.05) suggests temperature distributions differ across countries.
- We use **Kruskal–Wallis** if normality is questionable; otherwise **ANOVA**.
"""
        ),
        md_cell("## Vulnerability ranking (heuristic composite)"),
        code_cell(
            """\
rank_tbl = vulnerability_ranking(df_all)
rank_tbl
"""
        ),
        md_cell(
            """## COP32-oriented takeaways (fill from results)

- Which country is warming fastest: identify the top `warming_slope` in the ranking table.
- Which country has the most unstable precipitation: highest `precip_cv`.
- What extreme heat and drought reveal: compare `ExtremeHeatDays` and `DryDays`.
- How Ethiopia compares to neighbors: contrast Ethiopia vs Kenya/Sudan/Tanzania.
- Priority climate finance: pick highest composite vulnerability with a short justification.
"""
        ),
    ]
    return nb


def write_notebook(nb: nbf.NotebookNode, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


def main() -> None:
    nb_dir = paths().notebooks_dir

    for country in COUNTRIES:
        nb = build_country_eda_notebook(country)
        out_path = nb_dir / f"task2_eda_{country}.ipynb"
        write_notebook(nb, out_path)

    nb = build_task3_comparison_notebook()
    write_notebook(nb, nb_dir / "task3_country_comparison.ipynb")

    print("Generated notebooks in:", nb_dir)


if __name__ == "__main__":
    main()

