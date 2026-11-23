"""
Statistical and analytical computing utilities for Spotify Trends Analytics Studio.
"""
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

AUDIO_FEATURE_COLUMNS = [
    "danceability", "energy", "speechiness", "acousticness",
    "instrumentalness", "liveness", "valence"
]

ALL_FEATURE_COLUMNS = AUDIO_FEATURE_COLUMNS + ["loudness", "tempo"]


def compute_correlation_matrix(
    df: pd.DataFrame, 
    columns: Optional[List[str]] = None, 
    method: str = "pearson"
) -> pd.DataFrame:
    """
    Computes correlation matrix for specified numerical columns.
    """
    cols = columns or (ALL_FEATURE_COLUMNS + ["popularity", "streams"])
    valid_cols = [c for c in cols if c in df.columns]
    numeric_df = df[valid_cols].apply(pd.to_numeric, errors="coerce")
    return numeric_df.corr(method=method).round(3)


def calculate_feature_radar_data(df: pd.DataFrame, group_col: Optional[str] = None) -> pd.DataFrame:
    """
    Calculates average normalized audio features for radar/polar charts.
    """
    features = [f for f in AUDIO_FEATURE_COLUMNS if f in df.columns]
    if group_col and group_col in df.columns:
        radar_df = df.groupby(group_col)[features].mean().reset_index()
    else:
        avg_dict = {f: [df[f].mean()] for f in features if f in df.columns}
        radar_df = pd.DataFrame(avg_dict)
    return radar_df.round(3)


def get_feature_distribution_stats(df: pd.DataFrame, feature: str) -> Dict[str, Any]:
    """
    Computes distribution statistics (mean, median, std, min, max, IQR) for an audio feature.
    """
    if feature not in df.columns:
        return {}
    series = df[feature].dropna()
    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    return {
        "mean": round(float(series.mean()), 3),
        "median": round(float(series.median()), 3),
        "std": round(float(series.std()), 3),
        "min": round(float(series.min()), 3),
        "max": round(float(series.max()), 3),
        "q25": round(q25, 3),
        "q75": round(q75, 3),
        "iqr": round(q75 - q25, 3)
    }
