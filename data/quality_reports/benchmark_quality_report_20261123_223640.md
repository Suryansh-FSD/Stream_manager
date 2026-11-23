# Spotify Trends Data Quality Report
**Generated:** 2026-11-23T22:36:40.338501

## 1. Executive Summary
- **Total Input Records:** 44
- **Cleaned & Retained Records:** 40
- **Duplicates Removed:** 4
- **Track-Artist Collaboration Associations:** 66

## 2. Core Metrics Validation
| Metric | Evaluated | Invalid Count | Range / Bounds | Status |
|---|---|---|---|---|
| Popularity | 40 | 0 | [14.0 - 100.0] (Mean: 65.75) | ✅ PASS |
| Streams | 40 | 0 | Total: 95,213,858 | ✅ PASS |
| Release Date | 40 | 0 | Precisions: {'day': 26, 'year': 8, 'month': 6} | ✅ PASS |

## 3. Audio Features Range Verification
| Feature | Evaluated | Invalid Count | Min | Max | Mean | Verification |
|---|---|---|---|---|---|---|
| danceability | 40 | 0 | 0.258 | 0.899 | 0.646 | ✅ VALID |
| energy | 40 | 0 | 0.255 | 0.979 | 0.582 | ✅ VALID |
| speechiness | 40 | 0 | 0.02 | 0.391 | 0.087 | ✅ VALID |
| acousticness | 40 | 0 | 0.028 | 0.667 | 0.28 | ✅ VALID |
| instrumentalness | 40 | 0 | 0.001 | 0.375 | 0.108 | ✅ VALID |
| liveness | 40 | 0 | 0.03 | 0.82 | 0.156 | ✅ VALID |
| valence | 40 | 0 | 0.083 | 0.872 | 0.462 | ✅ VALID |
| tempo | 40 | 0 | 66.9 | 161.6 | 126.065 | ✅ VALID |

## 4. Statistical Outliers (IQR Method)
| Field | Outlier Count | Lower Bound | Upper Bound | Range Encountered |
|---|---|---|---|---|
| streams | 5 | -2174689.5 | 4436400.5 | [4610320.0 - 30200894.0] |
| popularity | 0 | 11.38 | 124.38 | None |
| duration_ms | 0 | 94325.5 | 321193.5 | None |
| tempo | 2 | 84.94 | 169.24 | [66.9 - 82.1] |

## 5. Pipeline Cleaning Decisions
- Mapped 22 columns from input: {'track_id': 'track_id', 'track_name': 'track_title', 'artist_name': 'artist_name', 'album_name': 'album_name', 'release_date': 'release_date', 'popularity': 'popularity', 'streams': 'streams', 'duration_ms': 'duration_ms', 'explicit': 'explicit', 'genre': 'genre', 'danceability': 'danceability', 'energy': 'energy', 'key': 'key', 'loudness': 'loudness', 'mode': 'mode', 'speechiness': 'speechiness', 'acousticness': 'acousticness', 'instrumentalness': 'instrumentalness', 'liveness': 'liveness', 'valence': 'valence', 'tempo': 'tempo', 'time_signature': 'time_signature'}
- Starting cleaning on 44 raw records.
- Processed streams column as numerical bigint without inferring from popularity.
- Detected and removed 4 duplicate track records.