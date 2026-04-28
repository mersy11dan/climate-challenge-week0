import pandas as pd

from src.cleaning import clean_country_dataframe


def test_clean_country_dataframe_smoke():
    raw = pd.DataFrame(
        {
            "YEAR": [2020, 2020, 2020],
            "DOY": [1, 2, 2],  # includes duplicate row potential
            "T2M": [25.0, -999, 26.0],
            "T2M_MAX": [36.0, 37.0, 37.0],
            "T2M_MIN": [20.0, 21.0, 21.0],
            "PRECTOTCORR": [0.0, 5.0, 5.0],
            "RH2M": [50.0, 55.0, 55.0],
            "WS2M": [2.0, 2.5, 2.5],
            "WS2M_MAX": [4.0, 4.2, 4.2],
        }
    )

    df, info = clean_country_dataframe(raw, "ethiopia", outlier_strategy="cap")

    assert "Country" in df.columns
    assert "DATE" in df.columns
    assert "Month" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["DATE"])
    assert df["Country"].iloc[0] == "ethiopia"
    assert info["duplicates_removed"] >= 0
    # Sentinel removed (may be forward-filled afterwards)
    assert (df["T2M"] == -999).sum() == 0

