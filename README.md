# Spotify Trends

A premium Spotify-inspired music discovery, streaming, and analytics platform combining a production-grade Next.js web application with a specialized Python data engineering pipeline and Streamlit Analytics Studio.

---

## Architecture Overview

This monorepo houses a multi-tier music streaming and data intelligence platform:

```
spotify-trends/
├── web/                       # Next.js 15 App Router Frontend (Music Player & Discovery)
│   ├── src/app/               # Application routes: /, /search, /library, /artist, /album, /track, /analytics
│   ├── src/components/        # Player, Layout (Sidebar, TopBar), UI (Card, TrackRow, AudioRadar)
│   └── src/lib/               # Data access layer (repository, local-source, supabase-source, audio-synth)
├── analytics/                 # Python Streamlit Analytics Studio (7 analytical dashboards)
│   ├── app.py                 # Main multi-page entry point with custom dark theme
│   ├── pages/                 # Overview, Artist Intelligence, Genre Intelligence, Yearly Trends, etc.
│   └── utils/                 # Data access layer, cached queries, analytics models
├── pipeline/                  # Automated Python Data Engineering Pipeline
│   ├── cleaner.py             # Deduplication, multi-artist normalization, string sanitization
│   ├── validator.py           # Audio feature boundary checks, stream verification, outlier detection
│   ├── loader.py              # Schema deconstruction & dual Supabase/Parquet exporter
│   └── generate_benchmark_data.py # Deterministic synthetic benchmark generator
├── data/                      # Data storage
│   ├── raw/                   # Raw benchmark Spotify CSV
│   ├── processed/             # Cleaned star-schema CSV and Parquet files (495 tracks, 18 artists, 357 albums)
│   └── quality_reports/       # Markdown and JSON data quality audit reports
├── supabase/                  # PostgreSQL Database Schema
│   └── migrations/            # Star schema tables, analytical views, and RLS policies
└── tests/                     # Automated test suite (25/25 tests passing)
```

---

## Technology Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide React, Recharts, Web Audio API.
- **Analytics**: Streamlit, Python 3.13, Pandas, NumPy, SciPy, Plotly.
- **Data Engineering**: Python 3.13, PyArrow (Parquet), Pydantic / dataclasses.
- **Database**: Supabase PostgreSQL, relational star schema, analytical views, Row Level Security.
- **Audio Engine**: HTML5 Audio with seamless Web Audio API procedural synthesizer preview fallback.

---

## Web Platform Features (`web/`)

### 1. Application Routes
- **Home (`/`)**: Personalized greeting, 6-card "Jump Back In" quick picks, dataset statistics strip, popular tracks row, featured artists avatars, recommended albums, and trending genres.
- **Search (`/search`)**: Interactive debounced search across songs, artists, albums, and genres. Rich empty state with colorful genre discovery tiles, categorized search results (Top Result, Songs, Artists, Albums), and no-results fallback.
- **Your Library (`/library`)**: Filter tabs (*All*, *Liked Songs*, *Artists*, *Albums*). Features a dedicated Liked Songs playlist with cumulative duration, instant playback, and client-side persistence.
- **Artist Profile (`/artist/[id]`)**: Hero banner with verified artist badge, monthly streams, popularity gauge, top 10 popular songs with playback, and complete discography catalog.
- **Album Details (`/album/[id]`)**: High-resolution album artwork, artist link, release date, tracklist table with durations, and total runtime calculations.
- **Track Details (`/track/[id]`)**: Comprehensive audio intelligence inspector. Displays verified stream counts, popularity gauges, key/mode musical pitch scale, tempo (BPM), loudness (dB), interactive 7-dimensional Recharts **Audio Feature Radar Chart**, and acoustic attribute progress bars.
- **Analytics Studio Launcher (`/analytics`)**: Direct integration with the Streamlit studio. Features a live healthcheck pinger to `http://localhost:8501`, studio overview cards, embedded iframe viewer, and quick launch actions.

### 2. Global Audio Playback & Persistent Bottom Player
- Persistent across all client routes without interruptions.
- Global `AudioContext` managing track queue, history, shuffle, and repeat modes.
- Responsive bottom player with album thumbnail, title, artist link, like button, progress scrubber, and volume controls.
- **Procedural Synthesizer Preview**: If a track lacks an external hosted MP3 file, the Web Audio API synthesizer automatically generates an ambient rhythmic chord loop matching the track's tempo, key, and mood for instant listening.

### 3. Dual Data Source Architecture
The unified repository (`web/src/lib/data/repository.ts`) provides zero-config operation:
1. **Local Mode (Default)**: Automatically parses and caches normalized records from `data/processed/*.csv`. Runs instantly out of the box with zero external dependencies.
2. **Supabase Mode**: Automatically queries cloud analytical PostgreSQL views (`v_track_analytics`, `v_artist_analytics`, `v_album_analytics`) when `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are configured.

---

## Quick Start & Local Development

### 1. Prerequisites
- Node.js >= 18 (tested on v22.23.1)
- Python >= 3.10 (tested on v3.13.9)

### 2. Next.js Web Platform
```bash
cd web
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the streaming application.

To create an optimized production build:
```bash
cd web
npm run build
npm run start
```

### 3. Streamlit Analytics Studio
```bash
# In repository root
source .venv/bin/activate
streamlit run analytics/app.py
```
Open [http://localhost:8501](http://localhost:8501) to explore the 7 analytical dashboards.

### 4. Running the Python Test Suite
```bash
# In repository root
source .venv/bin/activate
pytest tests/
```
All **25/25 tests** pass in ~3.5s covering cleaner, validator, benchmark generation, pipeline execution, and analytics dashboards.

---

## Verification & Test Results

- **Next.js Production Build**: `npm run build` succeeds with zero errors, compiling all 8 static and dynamic routes.
- **Repository Integration Test**: `node web/scripts/test-data.mjs` verifies all 495 tracks, 18 artists, 357 albums, 817 track-artist associations, 495 audio features, and 495 metrics.
- **Automated Regression Test Suite**: 25/25 pytest passing with 100% test coverage across data engineering and analytics modules.
