"""
Unified Data Source Abstraction for Spotify Trends Analytics Studio.
Supports local Parquet/CSV reads and optional Supabase PostgreSQL live connection.
Provides Streamlit caching, connection indicator, and fallback handling.
"""
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Try importing streamlit; if running in non-streamlit CLI/tests, use fallback pass-through cache
try:
    import streamlit as st
    cache_decorator = st.cache_data
except ImportError:
    def cache_decorator(**kwargs):
        def decorator(func):
            return func
        return decorator

# Path configurations
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
QUALITY_REPORTS_DIR = DATA_DIR / "quality_reports"

# Load environment
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)


class DataSource:
    def __init__(self):
        self.supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        self.mode = "local"
        self._supabase_client = None
        self._check_connection()

    def _check_connection(self) -> None:
        """Determines whether to operate in Supabase mode or Local Parquet mode."""
        if self.supabase_url and self.supabase_key and "your-project-id" not in self.supabase_url:
            try:
                from supabase import create_client
                self._supabase_client = create_client(self.supabase_url, self.supabase_key)
                self.mode = "supabase"
            except Exception:
                self.mode = "local"
        else:
            self.mode = "local"

    @property
    def is_supabase(self) -> bool:
        return self.mode == "supabase"


@cache_decorator(ttl=3600, show_spinner=False)
def load_processed_table(table_name: str) -> pd.DataFrame:
    """
    Loads a normalized table from data/processed/, preferring Parquet for speed with CSV fallback.
    """
    parquet_path = PROCESSED_DIR / f"{table_name}.parquet"
    csv_path = PROCESSED_DIR / f"{table_name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        # Return empty DataFrame with warning
        return pd.DataFrame()


@cache_decorator(ttl=3600, show_spinner=False)
def load_master_analytics_dataset() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and assembles the master joined track dataset for analytics.
    Joins tracks, albums, artists (primary), metrics, and audio features.
    Returns (master_df, source_metadata).
    """
    ds = DataSource()
    metadata: Dict[str, Any] = {
        "mode": ds.mode,
        "is_synthetic": True,
        "is_connected": ds.is_supabase,
        "record_count": 0,
        "processed_dir": str(PROCESSED_DIR.resolve())
    }

    # Load normalized tables
    df_tracks = load_processed_table("tracks")
    df_artists = load_processed_table("artists")
    df_albums = load_processed_table("albums")
    df_track_artists = load_processed_table("track_artists")
    df_audio = load_processed_table("audio_features")
    df_metrics = load_processed_table("track_metrics")

    if df_tracks.empty:
        return pd.DataFrame(), metadata

    # 1. Join tracks with albums
    master = df_tracks.copy()
    if not df_albums.empty:
        album_cols = ["id", "title", "release_date", "release_date_precision"]
        albums_clean = df_albums[[c for c in album_cols if c in df_albums.columns]].rename(
            columns={"title": "album_title"}
        )
        master = master.merge(albums_clean, left_on="album_id", right_on="id", how="left", suffixes=("", "_album"))

    # 2. Extract and join primary artist
    if not df_track_artists.empty and not df_artists.empty:
        primary_ta = df_track_artists[df_track_artists["is_primary"] == True].drop_duplicates(subset=["track_id"])
        artists_clean = df_artists[["id", "name", "genres"]].rename(
            columns={"name": "primary_artist_name", "genres": "artist_genres"}
        )
        primary_with_info = primary_ta.merge(artists_clean, left_on="artist_id", right_on="id", how="left")
        master = master.merge(
            primary_with_info[["track_id", "primary_artist_name", "artist_genres"]],
            left_on="id",
            right_on="track_id",
            how="left"
        )
    else:
        master["primary_artist_name"] = "Unknown Artist"
        master["artist_genres"] = [[]] * len(master)

    # 3. Join audio features
    if not df_audio.empty:
        audio_cols = [c for c in df_audio.columns if c != "track_id"]
        master = master.merge(df_audio, left_on="id", right_on="track_id", how="left")

    # 4. Join track metrics (popularity and streams)
    if not df_metrics.empty:
        metric_cols = ["track_id", "popularity", "streams"]
        master = master.merge(
            df_metrics[[c for c in metric_cols if c in df_metrics.columns]],
            left_on="id",
            right_on="track_id",
            how="left"
        )

    # Clean redundant join columns
    cols_to_drop = [c for c in master.columns if c.startswith("track_id_") or c in ["id_album", "id_y"]]
    master = master.drop(columns=cols_to_drop, errors="ignore")

    # Parse primary genre string from genres array or column
    def extract_first_genre(genres_val):
        if isinstance(genres_val, (list, np.ndarray)) and len(genres_val) > 0:
            return str(genres_val[0])
        elif isinstance(genres_val, str) and genres_val.strip():
            g_str = genres_val.strip("[]'\" ")
            parts = [p.strip(" '\"") for p in g_str.split(",") if p.strip(" '\"")]
            return parts[0] if parts else "Uncategorized"
        return "Uncategorized"

    if "artist_genres" in master.columns:
        master["primary_genre"] = master["artist_genres"].apply(extract_first_genre)
    else:
        master["primary_genre"] = "Uncategorized"

    # Extract release year
    if "release_date" in master.columns:
        master["release_year"] = pd.to_datetime(master["release_date"], errors="coerce").dt.year
    else:
        master["release_year"] = None

    metadata["record_count"] = len(master)
    return master, metadata


@cache_decorator(ttl=3600)
def load_latest_quality_report() -> Optional[Dict[str, Any]]:
    """
    Finds and loads the most recent JSON quality report in data/quality_reports/.
    """
    import json
    json_reports = sorted(QUALITY_REPORTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    if not json_reports:
        return None
    latest_file = json_reports[0]
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["_filepath"] = str(latest_file)
            return data
    except Exception:
        return None
