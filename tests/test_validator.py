"""
Automated unit tests for SpotifyDataValidator.
Tests bounds checking, missing values, outlier detection, and report rendering.
"""
import pytest
import pandas as pd
from pipeline.validator import SpotifyDataValidator
from pipeline.config import ValidationBounds


def test_popularity_range_validation():
    validator = SpotifyDataValidator()
    # 2 valid, 2 invalid
    df = pd.DataFrame({
        "popularity": [50, 95, -5, 120]
    })
    report = validator.validate_dataset(df, df, [], {})
    pop_res = report["range_validation"]["popularity"]
    assert pop_res["invalid_count"] == 2
    assert pop_res["min"] == -5
    assert pop_res["max"] == 120


def test_audio_feature_bounds_validation():
    validator = SpotifyDataValidator()
    df = pd.DataFrame({
        "danceability": [0.5, 0.95, 1.4], # 1 invalid (> 1.0)
        "energy": [0.2, -0.1, 0.8],        # 1 invalid (< 0.0)
        "tempo": [120.0, 95.0, 400.0]      # 1 invalid (> 350)
    })
    report = validator.validate_dataset(df, df, [], {})
    af_res = report["audio_feature_validation"]
    assert af_res["danceability"]["invalid_count"] == 1
    assert af_res["energy"]["invalid_count"] == 1
    assert af_res["tempo"]["invalid_count"] == 1


def test_missing_streams_not_inferred():
    validator = SpotifyDataValidator()
    # Streams column missing or containing NaNs
    df = pd.DataFrame({
        "popularity": [80, 90],
        "streams": [None, 500000]
    })
    report = validator.validate_dataset(df, df, [], {})
    assert report["missing_values"]["streams"]["missing_count"] == 1
    # Popularity should be evaluated separately
    assert report["range_validation"]["popularity"]["invalid_count"] == 0


def test_iqr_outlier_detection():
    validator = SpotifyDataValidator()
    # 20 regular stream values and 2 extreme outliers
    normal_streams = [100000 + i * 5000 for i in range(20)]
    streams_with_outliers = pd.Series(normal_streams + [50000000, 90000000])
    res = validator.detect_outliers_iqr(streams_with_outliers)
    assert res["count"] == 2
    assert res["max_outlier"] == 90000000


def test_report_generation(tmp_path):
    validator = SpotifyDataValidator()
    df = pd.DataFrame({
        "track_title": ["Alpha"],
        "artist_name": ["Beta"],
        "popularity": [75],
        "streams": [1500000],
        "danceability": [0.65]
    })
    report_dict = validator.validate_dataset(df, df, [], {"duplicates_removed": 0, "decisions": ["Test decision"]})
    json_path, md_path = validator.generate_reports(report_dict, output_prefix="test_report")

    assert json_path.exists()
    assert md_path.exists()
    md_content = md_path.read_text()
    assert "Spotify Trends Data Quality Report" in md_content
    assert "Test decision" in md_content
