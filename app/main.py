from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# #region agent log
def _agent_log(hypothesisId: str, location: str, message: str, data: dict) -> None:
    try:
        payload = {
            "sessionId": "46b3f0",
            "runId": "pre-fix",
            "hypothesisId": hypothesisId,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        root = Path(__file__).resolve().parents[1]
        (root / "debug-46b3f0.log").open("a", encoding="utf-8").write(json.dumps(payload) + "\n")
    except Exception:
        pass

_agent_log(
    "H1_import_path",
    "app/main.py:import",
    "Startup sys.path snapshot",
    {
        "cwd": os.getcwd(),
        "file": str(Path(__file__).resolve()),
        "root_guess": str(Path(__file__).resolve().parents[1]),
        "sys_path_head": sys.path[:8],
    },
)
# #endregion

try:
    from src.constants import COUNTRIES
    from src.paths import paths
    _agent_log("H2_import_ok", "app/main.py:import", "Imported src.* successfully", {})
except ModuleNotFoundError as e:
    _agent_log("H1_import_path", "app/main.py:import", "Import failed; attempting sys.path fix", {"error": repr(e)})
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    _agent_log("H3_path_injected", "app/main.py:import", "Injected project root into sys.path", {"project_root": project_root, "sys_path_head": sys.path[:8]})
    from src.constants import COUNTRIES
    from src.paths import paths
    _agent_log("H4_import_after_fix", "app/main.py:import", "Imported src.* after sys.path fix", {})


st.set_page_config(page_title="Climate Dashboard (Week 0)", layout="wide")


@st.cache_data
def load_cleaned(country: str) -> pd.DataFrame:
    p = paths().data_dir / f"{country}_clean.csv"
    if not p.exists():
        raise FileNotFoundError(
            f"Missing cleaned file: {p}. Run the Task 2 notebook for {country} first."
        )
    df = pd.read_csv(p, parse_dates=["DATE"])
    df["Country"] = country
    df["Year"] = pd.to_datetime(df["DATE"], errors="coerce").dt.year
    df["Month"] = pd.to_datetime(df["DATE"], errors="coerce").dt.month
    return df


st.title("Climate Challenge — Optional Dashboard")
st.caption("Reads cleaned datasets from `data/<country>_clean.csv` (kept out of Git).")

with st.sidebar:
    st.header("Filters")
    selected = st.multiselect(
        "Countries",
        options=COUNTRIES,
        default=COUNTRIES[:3],
    )

    if not selected:
        st.stop()

    # Determine year range across selected countries
    years = []
    for c in selected:
        try:
            d = load_cleaned(c)
            years.extend(d["Year"].dropna().astype(int).tolist())
        except FileNotFoundError:
            pass

    if not years:
        st.warning("No cleaned files found yet. Run the Task 2 notebooks to generate cleaned CSVs.")
        st.stop()

    y_min, y_max = int(min(years)), int(max(years))
    year_range = st.slider("Year range", min_value=y_min, max_value=y_max, value=(y_min, y_max))


dfs = [load_cleaned(c) for c in selected]
df_all = pd.concat(dfs, ignore_index=True)
df_all = df_all[df_all["Year"].between(year_range[0], year_range[1])]

tab1, tab2 = st.tabs(["Temperature trend", "Precipitation distribution"])

with tab1:
    st.subheader("Temperature trend (monthly average T2M)")
    monthly = (
        df_all.dropna(subset=["T2M", "Month"])
        .groupby(["Country", "Year", "Month"], as_index=False)["T2M"]
        .mean()
    )
    monthly["YearMonth"] = pd.to_datetime(
        monthly["Year"].astype(int).astype(str) + "-" + monthly["Month"].astype(int).astype(str).str.zfill(2) + "-01"
    )
    fig = px.line(
        monthly.sort_values(by="YearMonth"),
        x="YearMonth",
        y="T2M",
        color="Country",
        markers=False,
        title="Monthly average T2M",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Precipitation distribution (PRECTOTCORR)")
    fig = px.box(
        df_all.dropna(subset=["PRECTOTCORR"]),
        x="Country",
        y="PRECTOTCORR",
        points="outliers",
        title="Daily precipitation distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    """
### Notes
- This dashboard is intentionally simple and reproducible for Week 0.
- If you see missing-file errors, run the Task 2 notebooks to generate `data/*_clean.csv`.
"""
)