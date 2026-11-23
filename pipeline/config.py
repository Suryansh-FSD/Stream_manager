"""
Configuration and constants for the Spotify Trends Data Engineering Pipeline.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
QUALITY_REPORTS_DIR = DATA_DIR / "quality_reports"

# Load environment variables strictly from project .env if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)


# Ensure runtime directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
QUALITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ColumnMapping:
    """Flexible column mappings supporting diverse Spotify CSV formats."""
    track_id: List[str] = field(default_factory=lambda: [
        "track_id", "id", "spotify_id", "uri", "track_uri"
    ])
    track_title: List[str] = field(default_factory=lambda: [
        "track_title", "track_name", "title", "track", "song_name", "name"
    ])
    artist_name: List[str] = field(default_factory=lambda: [
        "artist_name", "artist(s)_name", "artists", "artist", "performer", "performers"
    ])
    album_name: List[str] = field(default_factory=lambda: [
        "album_name", "album", "release_name"
    ])
    release_date: List[str] = field(default_factory=lambda: [
        "release_date", "released_date", "date"
    ])
    release_year: List[str] = field(default_factory=lambda: [
        "released_year", "release_year", "year"
    ])
    release_month: List[str] = field(default_factory=lambda: [
        "released_month", "release_month", "month"
    ])
    release_day: List[str] = field(default_factory=lambda: [
        "released_day", "release_day", "day"
    ])
    popularity: List[str] = field(default_factory=lambda: [
        "popularity", "pop", "track_popularity"
    ])
    streams: List[str] = field(default_factory=lambda: [
        "streams", "stream_count", "play_count", "plays", "total_streams"
    ])
    duration_ms: List[str] = field(default_factory=lambda: [
        "duration_ms", "duration", "track_duration_ms", "duration_min"
    ])
    explicit: List[str] = field(default_factory=lambda: [
        "explicit", "is_explicit"
    ])
    genre: List[str] = field(default_factory=lambda: [
        "genre", "genres", "track_genre", "artist_genre", "top_genre"
    ])
    # Audio features
    danceability: List[str] = field(default_factory=lambda: ["danceability", "danceability_%", "dance"])
    energy: List[str] = field(default_factory=lambda: ["energy", "energy_%"])
    key: List[str] = field(default_factory=lambda: ["key"])
    loudness: List[str] = field(default_factory=lambda: ["loudness", "loudness_db"])
    mode: List[str] = field(default_factory=lambda: ["mode"])
    speechiness: List[str] = field(default_factory=lambda: ["speechiness", "speechiness_%"])
    acousticness: List[str] = field(default_factory=lambda: ["acousticness", "acousticness_%"])
    instrumentalness: List[str] = field(default_factory=lambda: ["instrumentalness", "instrumentalness_%"])
    liveness: List[str] = field(default_factory=lambda: ["liveness", "liveness_%"])
    valence: List[str] = field(default_factory=lambda: ["valence", "valence_%"])
    tempo: List[str] = field(default_factory=lambda: ["tempo", "bpm"])
    time_signature: List[str] = field(default_factory=lambda: ["time_signature"])


@dataclass
class ValidationBounds:
    """Numerical boundaries and validation limits."""
    popularity_min: int = 0
    popularity_max: int = 100
    streams_min: int = 0
    duration_ms_min: int = 1000  # Minimum 1 second
    duration_ms_max: int = 7200000  # Maximum 2 hours
    danceability_min: float = 0.0
    danceability_max: float = 1.0
    energy_min: float = 0.0
    energy_max: float = 1.0
    key_min: int = -1
    key_max: int = 11
    loudness_min: float = -60.0
    loudness_max: float = 5.0
    mode_values: List[int] = field(default_factory=lambda: [0, 1])
    speechiness_min: float = 0.0
    speechiness_max: float = 1.0
    acousticness_min: float = 0.0
    acousticness_max: float = 1.0
    instrumentalness_min: float = 0.0
    instrumentalness_max: float = 1.0
    liveness_min: float = 0.0
    liveness_max: float = 1.0
    valence_min: float = 0.0
    valence_max: float = 1.0
    tempo_min: float = 10.0
    tempo_max: float = 350.0
    time_signature_min: int = 1
    time_signature_max: int = 7


@dataclass
class PipelineConfig:
    """Overall pipeline settings and Supabase environment configuration."""
    column_mapping: ColumnMapping = field(default_factory=ColumnMapping)
    bounds: ValidationBounds = field(default_factory=ValidationBounds)
    supabase_url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    batch_size: int = 500
    z_score_threshold: float = 3.0
    iqr_multiplier: float = 1.5
