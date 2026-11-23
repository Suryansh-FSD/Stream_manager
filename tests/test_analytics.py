"""
Unit and integration tests for Spotify Trends Analytics Studio.
Verifies data loading, statistical calculations, formatting, queries, and AppTest execution.
"""
import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest

from analytics.utils.formatting import format_number, format_duration, format_percentage
from analytics.utils.analytics import (
    compute_correlation_matrix,
    calculate_feature_radar_data,
    get_feature_distribution_stats,
    AUDIO_FEATURE_COLUMNS
)
from analytics.utils.data_source import load_master_analytics_dataset, load_latest_quality_report
from analytics.utils.queries import (
    apply_global_filters,
    get_executive_kpis,
    get_top_tracks_by_streams,
    get_top_artists_by_streams,
    get_genre_metrics_summary,
    get_yearly_cohort_summary
)


def test_formatting_utilities():
    """Verifies human-readable formatting of numbers, durations, and percentages."""
    assert format_number(1_250_000_000) == "1.25B"
    assert format_number(12_400_000) == "12.4M"
    assert format_number(3_500) == "3.5K"
    assert format_number(42) == "42"
    assert format_number(None) == "N/A"

    assert format_duration(214_000) == "3:34"
    assert format_duration(65_000) == "1:05"
    assert format_duration(None) == "--:--"

    assert format_percentage(0.854) == "85.4%"
    assert format_percentage(None) == "N/A"


def test_master_dataset_loading():
    """Verifies master analytical dataset assembly from processed data."""
    df, meta = load_master_analytics_dataset()
    assert not df.empty, "Master analytics dataset must not be empty"
    assert len(df) == 495, f"Expected 495 clean tracks, got {len(df)}"
    assert meta["mode"] == "local"
    assert meta["is_synthetic"] is True

    required_columns = [
        "id", "title", "primary_artist_name", "album_title",
        "release_year", "primary_genre", "streams", "popularity",
        "danceability", "energy", "valence", "tempo"
    ]
    for col in required_columns:
        assert col in df.columns, f"Missing required analytical column: {col}"


def test_analytical_queries():
    """Verifies KPIs and analytical aggregations."""
    df, _ = load_master_analytics_dataset()

    # Executive KPIs
    kpis = get_executive_kpis(df)
    assert kpis["total_tracks"] == 495
    assert kpis["total_streams"] > 0
    assert kpis["unique_artists"] > 0
    assert kpis["unique_genres"] > 0
    assert 0 <= kpis["avg_popularity"] <= 100

    # Top Tracks
    top_tracks = get_top_tracks_by_streams(df, limit=10)
    assert len(top_tracks) == 10
    assert top_tracks["streams"].is_monotonic_decreasing

    # Top Artists (Primary Attribution)
    top_artists = get_top_artists_by_streams(df, limit=10)
    assert len(top_artists) == 10
    assert "total_streams" in top_artists.columns
    assert top_artists["total_streams"].is_monotonic_decreasing

    # Genre Intelligence Summary
    genre_sum = get_genre_metrics_summary(df)
    assert not genre_sum.empty
    assert "track_count" in genre_sum.columns

    # Yearly Cohort Summary
    yearly = get_yearly_cohort_summary(df)
    assert not yearly.empty
    assert "release_year" in yearly.columns


def test_global_filtering():
    """Verifies that global sidebar filters correctly subset the data."""
    df, _ = load_master_analytics_dataset()

    # Filter by genre
    unique_genres = df["primary_genre"].dropna().unique().tolist()
    assert len(unique_genres) > 1
    selected = [unique_genres[0]]
    filtered = apply_global_filters(df, selected_genres=selected)
    assert not filtered.empty
    assert (filtered["primary_genre"] == selected[0]).all()

    # Filter by popularity range
    filtered_pop = apply_global_filters(df, popularity_range=(70, 90))
    assert (filtered_pop["popularity"] >= 70).all()
    assert (filtered_pop["popularity"] <= 90).all()


def test_statistical_calculations():
    """Verifies correlation matrix, distribution stats, and radar profile."""
    df, _ = load_master_analytics_dataset()

    # Correlation Matrix
    corr = compute_correlation_matrix(df)
    assert not corr.empty
    assert "popularity" in corr.columns
    assert "danceability" in corr.columns
    assert corr.loc["popularity", "popularity"] == pytest.approx(1.0)

    # Feature Distribution Stats
    stats = get_feature_distribution_stats(df, "energy")
    assert "mean" in stats
    assert "median" in stats
    assert "iqr" in stats
    assert stats["min"] <= stats["median"] <= stats["max"]

    # Radar profile
    radar = calculate_feature_radar_data(df)
    assert not radar.empty
    for feat in AUDIO_FEATURE_COLUMNS:
        if feat in df.columns:
            assert feat in radar.columns


def test_quality_report_loader():
    """Verifies that the data quality JSON report is loaded successfully."""
    report = load_latest_quality_report()
    assert report is not None
    assert "summary" in report
    assert report["summary"]["total_input_records"] >= 1
    assert "cleaned_records" in report["summary"]


def test_streamlit_app_and_all_pages():
    """Integration test: runs Streamlit AppTest across all 7 dashboard pages."""
    from pathlib import Path
    app_path = Path(__file__).parent.parent / "analytics/app.py"
    pages = [
        "Music Industry Overview",
        "Artist Intelligence",
        "Genre Intelligence",
        "Yearly Music Trends",
        "Audio Feature Analysis",
        "Popularity & Correlation",
        "Data Quality & Report"
    ]

    at = AppTest.from_file(str(app_path.resolve()), default_timeout=30)
    at.run()
    assert not at.exception, f"App execution failed on default page: {at.exception}"

    for page in pages[1:]:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, f"App execution failed on page {page}: {at.exception}"
