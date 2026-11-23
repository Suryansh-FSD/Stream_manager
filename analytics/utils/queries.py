"""
Analytical query and filtering functions for Spotify Trends Analytics Studio.
Operates on the assembled master DataFrame with filter isolation and aggregation.
"""
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np


def apply_global_filters(
    df: pd.DataFrame,
    year_range: Optional[Tuple[int, int]] = None,
    selected_genres: Optional[List[str]] = None,
    selected_artists: Optional[List[str]] = None,
    popularity_range: Optional[Tuple[int, int]] = None
) -> pd.DataFrame:
    """
    Applies global sidebar filter selections to the master analytical dataset.
    """
    if df.empty:
        return df

    filtered = df.copy()

    # Filter release year
    if year_range and "release_year" in filtered.columns:
        filtered = filtered[
            (filtered["release_year"].isna()) |
            ((filtered["release_year"] >= year_range[0]) & (filtered["release_year"] <= year_range[1]))
        ]

    # Filter genres
    if selected_genres and "primary_genre" in filtered.columns:
        if "All Genres" not in selected_genres and len(selected_genres) > 0:
            filtered = filtered[filtered["primary_genre"].isin(selected_genres)]

    # Filter artists
    if selected_artists and "primary_artist_name" in filtered.columns:
        if "All Artists" not in selected_artists and len(selected_artists) > 0:
            filtered = filtered[filtered["primary_artist_name"].isin(selected_artists)]

    # Filter popularity
    if popularity_range and "popularity" in filtered.columns:
        filtered = filtered[
            (filtered["popularity"].isna()) |
            ((filtered["popularity"] >= popularity_range[0]) & (filtered["popularity"] <= popularity_range[1]))
        ]

    return filtered


def get_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates top-level executive KPIs for the Overview page."""
    if df.empty:
        return {
            "total_tracks": 0,
            "total_streams": 0,
            "unique_artists": 0,
            "unique_genres": 0,
            "avg_popularity": 0.0,
            "avg_duration_sec": 0
        }

    total_tracks = len(df)
    total_streams = int(df["streams"].sum()) if "streams" in df.columns and df["streams"].notna().any() else 0
    unique_artists = df["primary_artist_name"].nunique() if "primary_artist_name" in df.columns else 0
    unique_genres = df["primary_genre"].nunique() if "primary_genre" in df.columns else 0
    avg_pop = round(float(df["popularity"].mean()), 1) if "popularity" in df.columns and df["popularity"].notna().any() else 0.0
    avg_duration = int(df["duration_ms"].mean() // 1000) if "duration_ms" in df.columns and df["duration_ms"].notna().any() else 0

    return {
        "total_tracks": total_tracks,
        "total_streams": total_streams,
        "unique_artists": unique_artists,
        "unique_genres": unique_genres,
        "avg_popularity": avg_pop,
        "avg_duration_sec": avg_duration
    }


def get_top_tracks_by_streams(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Returns top tracks ranked by actual streams."""
    if df.empty or "streams" not in df.columns:
        return pd.DataFrame()
    cols = ["title", "primary_artist_name", "album_title", "streams", "popularity", "primary_genre"]
    available_cols = [c for c in cols if c in df.columns]
    return df.sort_values(by="streams", ascending=False).head(limit)[available_cols]


def get_top_artists_by_streams(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Returns top artists ranked by total streams using primary-artist attribution
    to avoid collaborative double-counting.
    """
    if df.empty or "primary_artist_name" not in df.columns or "streams" not in df.columns:
        return pd.DataFrame()
    
    artist_agg = df.groupby("primary_artist_name").agg(
        total_streams=("streams", "sum"),
        track_count=("id", "count"),
        avg_popularity=("popularity", "mean")
    ).reset_index()

    artist_agg["avg_popularity"] = artist_agg["avg_popularity"].round(1)
    return artist_agg.sort_values(by="total_streams", ascending=False).head(limit)


def get_genre_metrics_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates streams, popularity, and audio features by primary genre."""
    if df.empty or "primary_genre" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "id": "count",
        "streams": "sum",
        "popularity": "mean"
    }
    for feat in ["danceability", "energy", "valence", "tempo"]:
        if feat in df.columns:
            agg_dict[feat] = "mean"

    summary = df.groupby("primary_genre").agg(agg_dict).reset_index()
    summary = summary.rename(columns={"id": "track_count"})
    summary["popularity"] = summary["popularity"].round(1)
    for feat in ["danceability", "energy", "valence"]:
        if feat in summary.columns:
            summary[feat] = summary[feat].round(3)
    if "tempo" in summary.columns:
        summary["tempo"] = summary["tempo"].round(1)

    return summary.sort_values(by="streams", ascending=False)


def get_yearly_cohort_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates release-year cohorts (track volume, popularity, audio features)."""
    if df.empty or "release_year" not in df.columns:
        return pd.DataFrame()

    valid_years = df.dropna(subset=["release_year"]).copy()
    valid_years["release_year"] = valid_years["release_year"].astype(int)

    agg_dict = {
        "id": "count",
        "popularity": "mean",
        "streams": "sum"
    }
    for feat in ["danceability", "energy", "acousticness", "valence"]:
        if feat in valid_years.columns:
            agg_dict[feat] = "mean"

    yearly = valid_years.groupby("release_year").agg(agg_dict).reset_index()
    yearly = yearly.rename(columns={"id": "track_count"})
    yearly["popularity"] = yearly["popularity"].round(1)
    for feat in ["danceability", "energy", "acousticness", "valence"]:
        if feat in yearly.columns:
            yearly[feat] = yearly[feat].round(3)

    return yearly.sort_values(by="release_year")
