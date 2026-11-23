# Spotify Trends Data Quality Report
**Generated:** 2026-11-23T23:24:01.405341

## 1. Executive Summary
- **Total Input Records:** 22
- **Cleaned & Retained Records:** 20
- **Duplicates Removed:** 2
- **Track-Artist Collaboration Associations:** 35

## 2. Core Metrics Validation
| Metric | Evaluated | Invalid Count | Range / Bounds | Status |
|---|---|---|---|---|
| Popularity | 20 | 0 | [46.0 - 98.0] (Mean: 66.4) | ✅ PASS |
| Streams | 20 | 0 | Total: 79,248,856 | ✅ PASS |
| Release Date | 20 | 0 | Precisions: {'day': 14, 'year': 4, 'month': 2} | ✅ PASS |

## 3. Audio Features Range Verification
| Feature | Evaluated | Invalid Count | Min | Max | Mean | Verification |
|---|---|---|---|---|---|---|
| danceability | 20 | 0 | 0.277 | 0.879 | 0.596 | ✅ VALID |
| energy | 20 | 0 | 0.142 | 0.829 | 0.588 | ✅ VALID |
| speechiness | 20 | 0 | 0.02 | 0.21 | 0.068 | ✅ VALID |
| acousticness | 20 | 0 | 0.075 | 0.498 | 0.272 | ✅ VALID |
| instrumentalness | 20 | 0 | 0.013 | 0.597 | 0.206 | ✅ VALID |
| liveness | 20 | 0 | 0.03 | 0.265 | 0.095 | ✅ VALID |
| valence | 20 | 0 | 0.183 | 0.952 | 0.502 | ✅ VALID |
| tempo | 20 | 0 | 77.0 | 164.1 | 117.85 | ✅ VALID |

## 4. Statistical Outliers (IQR Method)
| Field | Outlier Count | Lower Bound | Upper Bound | Range Encountered |
|---|---|---|---|---|
| streams | 3 | -1460197.0 | 3454635.0 | [6927708.0 - 46098170.0] |
| popularity | 0 | 25.12 | 102.12 | None |
| duration_ms | 1 | 150766.0 | 273634.0 | [293135.0 - 293135.0] |
| tempo | 0 | 36.46 | 197.56 | None |

## 5. Pipeline Cleaning Decisions
- Mapped 22 columns from input: {'track_id': 'track_id', 'track_name': 'track_title', 'artist_name': 'artist_name', 'album_name': 'album_name', 'release_date': 'release_date', 'popularity': 'popularity', 'streams': 'streams', 'duration_ms': 'duration_ms', 'explicit': 'explicit', 'genre': 'genre', 'danceability': 'danceability', 'energy': 'energy', 'key': 'key', 'loudness': 'loudness', 'mode': 'mode', 'speechiness': 'speechiness', 'acousticness': 'acousticness', 'instrumentalness': 'instrumentalness', 'liveness': 'liveness', 'valence': 'valence', 'tempo': 'tempo', 'time_signature': 'time_signature'}
- Starting cleaning on 22 raw records.
- Processed streams column as numerical bigint without inferring from popularity.
- Detected and removed 2 duplicate track records.