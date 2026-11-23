"""
Automated unit tests for SpotifyDataCleaner.
Tests duplicate detection, multi-artist parsing, date precision, and column standardization.
"""
import pytest
import pandas as pd
from pipeline.cleaner import SpotifyDataCleaner
from pipeline.config import ColumnMapping


def test_standardize_column_names():
    cleaner = SpotifyDataCleaner()
    df = pd.DataFrame({
        "Track Name": ["Midnight City"],
        "Artist(s)_Name": ["M83"],
        "Released_Year": [2011],
        "BPM": [105]
    })
    standardized_df, mapping = cleaner.standardize_column_names(df)
    assert "track_title" in standardized_df.columns
    assert "artist_name" in standardized_df.columns
    assert "release_year" in standardized_df.columns
    assert "tempo" in standardized_df.columns


def test_split_artists_collaborations():
    cleaner = SpotifyDataCleaner()
    
    # Single artist
    res1 = cleaner.split_artists("The Weeknd")
    assert len(res1) == 1
    assert res1[0]["name"] == "The Weeknd"
    assert res1[0]["is_primary"] is True
    assert res1[0]["role"] == "main"

    # Featured collaboration
    res2 = cleaner.split_artists("Solaris feat. Echo & The Drift")
    assert len(res2) >= 2
    assert res2[0]["name"] == "Solaris"
    assert res2[0]["is_primary"] is True
    assert res2[1]["is_primary"] is False
    assert res2[1]["role"] == "featured"

    # Band with slash protected (AC/DC)
    res3 = cleaner.split_artists("AC/DC")
    assert len(res3) == 1
    assert res3[0]["name"] == "AC/DC"


def test_parse_release_date_variations():
    cleaner = SpotifyDataCleaner()

    # Full date string
    row_day = pd.Series({"release_date": "2023-04-15"})
    d_str, prec = cleaner.parse_release_date(row_day)
    assert d_str == "2023-04-15"
    assert prec == "day"

    # Year-month string
    row_month = pd.Series({"release_date": "2021-09"})
    d_str, prec = cleaner.parse_release_date(row_month)
    assert d_str == "2021-09-01"
    assert prec == "month"

    # Year only string
    row_year = pd.Series({"release_date": "2018"})
    d_str, prec = cleaner.parse_release_date(row_year)
    assert d_str == "2018-01-01"
    assert prec == "year"

    # Split year/month/day columns
    row_split = pd.Series({"release_year": 2020, "release_month": 6, "release_day": 21})
    d_str, prec = cleaner.parse_release_date(row_split)
    assert d_str == "2020-06-21"
    assert prec == "day"


def test_duplicate_detection_and_removal():
    cleaner = SpotifyDataCleaner()
    df = pd.DataFrame({
        "track_title": ["Starlight", "Starlight", "Solar Drift"],
        "artist_name": ["Muse", "Muse", "Solaris"],
        "streams": ["500000", "1000000", "250000"],
        "popularity": [70, 85, 60]
    })
    cleaned_df, raw_df, associations, meta = cleaner.clean_dataset(df)

    assert len(cleaned_df) == 2
    assert meta["duplicates_removed"] == 1
    # Verify the higher stream/popularity record was kept
    muse_record = cleaned_df[cleaned_df["artist_name"] == "Muse"].iloc[0]
    assert muse_record["streams"] == 1000000
    assert muse_record["popularity"] == 85


def test_percentage_audio_feature_normalization():
    cleaner = SpotifyDataCleaner()
    df = pd.DataFrame({
        "track_name": ["Vibe"],
        "artist_name": ["Aura"],
        "danceability_%": [75.0],
        "energy_%": [92.0]
    })
    cleaned_df, _, _, _ = cleaner.clean_dataset(df)
    assert cleaned_df["danceability"].iloc[0] == 0.75
    assert cleaned_df["energy"].iloc[0] == 0.92
