# Spotify Trends Data Quality Report
**Generated:** 2026-11-25T22:16:18.304677

## 1. Executive Summary
- **Total Input Records:** 505
- **Cleaned & Retained Records:** 495
- **Duplicates Removed:** 10
- **Track-Artist Collaboration Associations:** 817

## 2. Core Metrics Validation
| Metric | Evaluated | Invalid Count | Range / Bounds | Status |
|---|---|---|---|---|
| Popularity | 495 | 0 | [12.0 - 100.0] (Mean: 64.98) | ✅ PASS |
| Streams | 495 | 0 | Total: 907,859,465 | ✅ PASS |
| Release Date | 495 | 0 | Precisions: {'day': 355, 'year': 77, 'month': 63} | ✅ PASS |

## 3. Audio Features Range Verification
| Feature | Evaluated | Invalid Count | Min | Max | Mean | Verification |
|---|---|---|---|---|---|---|
| danceability | 495 | 0 | 0.143 | 0.97 | 0.63 | ✅ VALID |
| energy | 495 | 0 | 0.093 | 0.972 | 0.569 | ✅ VALID |
| speechiness | 495 | 0 | 0.02 | 0.432 | 0.081 | ✅ VALID |
| acousticness | 495 | 0 | 0.005 | 0.792 | 0.289 | ✅ VALID |
| instrumentalness | 495 | 0 | 0.0 | 0.95 | 0.141 | ✅ VALID |
| liveness | 495 | 0 | 0.03 | 0.785 | 0.117 | ✅ VALID |
| valence | 495 | 0 | 0.05 | 0.947 | 0.489 | ✅ VALID |
| tempo | 495 | 0 | 60.0 | 193.6 | 120.185 | ✅ VALID |

## 4. Statistical Outliers (IQR Method)
| Field | Outlier Count | Lower Bound | Upper Bound | Range Encountered |
|---|---|---|---|---|
| streams | 51 | -1821834.25 | 4058387.75 | [4081276.0 - 60082159.0] |
| popularity | 4 | 17.25 | 111.25 | [12.0 - 17.0] |
| duration_ms | 3 | 118062.25 | 304196.25 | [85471.0 - 326559.0] |
| tempo | 2 | 56.2 | 185.0 | [185.5 - 193.6] |

## 5. Pipeline Cleaning Decisions
- Mapped 22 columns from input: {'track_id': 'track_id', 'track_name': 'track_title', 'artist_name': 'artist_name', 'album_name': 'album_name', 'release_date': 'release_date', 'popularity': 'popularity', 'streams': 'streams', 'duration_ms': 'duration_ms', 'explicit': 'explicit', 'genre': 'genre', 'danceability': 'danceability', 'energy': 'energy', 'key': 'key', 'loudness': 'loudness', 'mode': 'mode', 'speechiness': 'speechiness', 'acousticness': 'acousticness', 'instrumentalness': 'instrumentalness', 'liveness': 'liveness', 'valence': 'valence', 'tempo': 'tempo', 'time_signature': 'time_signature'}
- Starting cleaning on 505 raw records.
- Processed streams column as numerical bigint without inferring from popularity.
- Detected and removed 10 duplicate track records.