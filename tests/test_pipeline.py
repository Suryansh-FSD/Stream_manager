"""
Automated integration tests for the full Spotify Trends Data Engineering Pipeline.
Tests end-to-end execution, local Parquet/CSV export, idempotency, and error handling.
"""
import pytest
from pathlib import Path
import pandas as pd

from pipeline.generate_benchmark_data import generate_synthetic_benchmark_dataset
from pipeline.run_pipeline import run_pipeline
from pipeline.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, QUALITY_REPORTS_DIR
from pipeline.loader import SupabaseLoader


@pytest.fixture(scope="module", autouse=True)
def preserve_master_benchmark_dataset():
    """Restores master benchmark dataset after pipeline integration tests finish."""
    yield
    raw_benchmark = RAW_DATA_DIR / "benchmark_spotify.csv"
    if raw_benchmark.exists():
        run_pipeline(str(raw_benchmark), is_benchmark=True, load_supabase=False)


def test_end_to_end_pipeline_with_benchmark_data(tmp_path):
    # 1. Generate test benchmark CSV
    test_csv = tmp_path / "test_benchmark.csv"
    df = generate_synthetic_benchmark_dataset(record_count=40, seed=123)
    df.to_csv(test_csv, index=False)

    # 2. Run pipeline
    exit_code = run_pipeline(str(test_csv), is_benchmark=True, load_supabase=False)
    assert exit_code == 0

    # 3. Verify exported entities exist in data/processed/
    expected_entities = ["tracks", "artists", "albums", "track_artists", "audio_features", "track_metrics"]
    for ent in expected_entities:
        csv_file = PROCESSED_DATA_DIR / f"{ent}.csv"
        parquet_file = PROCESSED_DATA_DIR / f"{ent}.parquet"
        assert csv_file.exists(), f"Missing exported CSV: {csv_file}"
        assert parquet_file.exists(), f"Missing exported Parquet: {parquet_file}"

        # Check records
        loaded_df = pd.read_parquet(parquet_file)
        assert len(loaded_df) > 0

    # 4. Verify quality report was generated
    report_files = list(QUALITY_REPORTS_DIR.glob("benchmark_quality_report_*.json"))
    assert len(report_files) > 0


def test_pipeline_idempotency_on_repeated_runs(tmp_path):
    test_csv = tmp_path / "idempotent_test.csv"
    df = generate_synthetic_benchmark_dataset(record_count=20, seed=999)
    df.to_csv(test_csv, index=False)

    # Run twice
    code1 = run_pipeline(str(test_csv), is_benchmark=True, load_supabase=False)
    code2 = run_pipeline(str(test_csv), is_benchmark=True, load_supabase=False)
    assert code1 == 0
    assert code2 == 0


def test_pipeline_handles_missing_file():
    missing_path = "/path/to/non_existent_spotify_file.csv"
    exit_code = run_pipeline(missing_path)
    assert exit_code == 1


def test_loader_referential_integrity():
    cleaner_output = pd.DataFrame({
        "track_id": ["t1", "t2"],
        "track_title": ["Track One", "Track Two"],
        "primary_artist": ["Artist A", "Artist B"],
        "album_name": ["Album A", "Album B"],
        "popularity": [80, 70],
        "streams": [100000, 200000],
        "genre": ["Pop", "Rock"]
    })
    track_artists_records = [
        {"track_id": "t1", "artist_id": "a1", "artist_name": "Artist A", "role": "main", "is_primary": True},
        {"track_id": "t1", "artist_id": "a2", "artist_name": "Artist B", "role": "featured", "is_primary": False},
        {"track_id": "t2", "artist_id": "a2", "artist_name": "Artist B", "role": "main", "is_primary": True}
    ]

    entities = SupabaseLoader.prepare_relational_tables(cleaner_output, track_artists_records)
    
    # Check that artist_id in track_artists match artists table
    artist_ids = set(entities["artists"]["id"])
    for ta_artist_id in entities["track_artists"]["artist_id"]:
        assert ta_artist_id in artist_ids

    # Check track_id in track_artists match tracks table
    track_ids = set(entities["tracks"]["id"])
    for ta_track_id in entities["track_artists"]["track_id"]:
        assert ta_track_id in track_ids
