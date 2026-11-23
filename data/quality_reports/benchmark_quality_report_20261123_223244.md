# Spotify Trends Data Quality Report
**Generated:** 2026-11-23T22:32:44.182746

## 1. Executive Summary
- **Total Input Records:** 305
- **Cleaned & Retained Records:** 299
- **Duplicates Removed:** 6
- **Track-Artist Collaboration Associations:** 504

## 2. Core Metrics Validation
| Metric | Evaluated | Invalid Count | Range / Bounds | Status |
|---|---|---|---|---|
| Popularity | 299 | 0 | [12.0 - 100.0] (Mean: 65.83) | ✅ PASS |
| Streams | 299 | 0 | Total: 522,358,910 | ✅ PASS |
| Release Date | 299 | 0 | Precisions: {'day': 214, 'year': 46, 'month': 39} | ✅ PASS |

## 3. Audio Features Range Verification
| Feature | Evaluated | Invalid Count | Min | Max | Mean | Verification |
|---|---|---|---|---|---|---|
| danceability | 299 | 0 | 0.143 | 0.948 | 0.63 | ✅ VALID |
| energy | 299 | 0 | 0.093 | 0.972 | 0.569 | ✅ VALID |
| speechiness | 299 | 0 | 0.02 | 0.432 | 0.082 | ✅ VALID |
| acousticness | 299 | 0 | 0.019 | 0.792 | 0.287 | ✅ VALID |
| instrumentalness | 299 | 0 | 0.0 | 0.95 | 0.131 | ✅ VALID |
| liveness | 299 | 0 | 0.03 | 0.785 | 0.121 | ✅ VALID |
| valence | 299 | 0 | 0.05 | 0.947 | 0.497 | ✅ VALID |
| tempo | 299 | 0 | 60.0 | 193.6 | 120.61 | ✅ VALID |

## 4. Statistical Outliers (IQR Method)
| Field | Outlier Count | Lower Bound | Upper Bound | Range Encountered |
|---|---|---|---|---|
| streams | 29 | -1781290.5 | 3958401.5 | [4151339.0 - 34422981.0] |
| popularity | 1 | 17.5 | 113.5 | [12.0 - 12.0] |
| duration_ms | 2 | 121598.25 | 300696.25 | [112128.0 - 326559.0] |
| tempo | 1 | 55.28 | 187.07 | [193.6 - 193.6] |

## 5. Pipeline Cleaning Decisions
- Mapped 22 columns from input: {'track_id': 'track_id', 'track_name': 'track_title', 'artist_name': 'artist_name', 'album_name': 'album_name', 'release_date': 'release_date', 'popularity': 'popularity', 'streams': 'streams', 'duration_ms': 'duration_ms', 'explicit': 'explicit', 'genre': 'genre', 'danceability': 'danceability', 'energy': 'energy', 'key': 'key', 'loudness': 'loudness', 'mode': 'mode', 'speechiness': 'speechiness', 'acousticness': 'acousticness', 'instrumentalness': 'instrumentalness', 'liveness': 'liveness', 'valence': 'valence', 'tempo': 'tempo', 'time_signature': 'time_signature'}
- Starting cleaning on 305 raw records.
- Processed streams column as numerical bigint without inferring from popularity.
- Detected and removed 6 duplicate track records.