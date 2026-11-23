"""
Automated unit tests for synthetic benchmark dataset generator.
Verifies determinism, column integrity, multi-artist collaborations, and synthetic disclaimers.
"""
import pytest
import pandas as pd
from pipeline.generate_benchmark_data import generate_synthetic_benchmark_dataset, RANDOM_SEED


def test_benchmark_generation_determinism():
    df1 = generate_synthetic_benchmark_dataset(record_count=50, seed=42)
    df2 = generate_synthetic_benchmark_dataset(record_count=50, seed=42)
    pd.testing.assert_frame_equal(df1, df2)


def test_benchmark_contains_required_fields():
    df = generate_synthetic_benchmark_dataset(record_count=30, seed=RANDOM_SEED)
    required_cols = [
        "track_id", "track_name", "artist_name", "album_name", "release_date",
        "popularity", "streams", "duration_ms", "explicit", "genre",
        "danceability", "energy", "key", "loudness", "mode", "speechiness",
        "acousticness", "instrumentalness", "liveness", "valence", "tempo",
        "time_signature", "is_synthetic_benchmark"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required benchmark column: {col}"

    assert (df["is_synthetic_benchmark"] == True).all()


def test_benchmark_multi_artist_and_genre_diversity():
    df = generate_synthetic_benchmark_dataset(record_count=100, seed=RANDOM_SEED)
    
    # Check that multiple genres exist
    unique_genres = df["genre"].nunique()
    assert unique_genres >= 5

    # Check that collaborations (feat., &, comma) exist in artist names
    collaborations = df[df["artist_name"].str.contains(r"feat\.|&|,", regex=True)]
    assert len(collaborations) > 0


def test_benchmark_streams_and_popularity_separation():
    df = generate_synthetic_benchmark_dataset(record_count=50, seed=RANDOM_SEED)
    # Popularity must be within [0, 100]
    assert df["popularity"].min() >= 0
    assert df["popularity"].max() <= 100

    # Streams must be substantial (power-law distribution > 50,000)
    assert df["streams"].min() > 50000
    # Streams must NOT be identical to popularity
    assert (df["streams"] != df["popularity"]).all()
