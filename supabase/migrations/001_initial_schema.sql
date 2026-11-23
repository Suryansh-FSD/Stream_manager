-- ==============================================================================
-- Migration 001: Initial Normalized Relational & Star Schema for Spotify Trends
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Artists Table
CREATE TABLE IF NOT EXISTS artists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    spotify_artist_id TEXT UNIQUE,
    name TEXT NOT NULL,
    genres TEXT[] DEFAULT '{}',
    popularity INTEGER CHECK (popularity >= 0 AND popularity <= 100),
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Albums Table
CREATE TABLE IF NOT EXISTS albums (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    spotify_album_id TEXT UNIQUE,
    title TEXT NOT NULL,
    artist_id UUID REFERENCES artists(id) ON DELETE SET NULL,
    release_date DATE,
    release_date_precision TEXT CHECK (release_date_precision IN ('year', 'month', 'day')),
    total_tracks INTEGER DEFAULT 1,
    cover_image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Tracks Table
CREATE TABLE IF NOT EXISTS tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    spotify_track_id TEXT UNIQUE,
    isrc TEXT,
    title TEXT NOT NULL,
    album_id UUID REFERENCES albums(id) ON DELETE CASCADE,
    duration_ms INTEGER NOT NULL CHECK (duration_ms > 0),
    explicit BOOLEAN DEFAULT FALSE,
    preview_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Track Artists Junction Table (Handles collaborations cleanly without multiplying stream totals)
CREATE TABLE IF NOT EXISTS track_artists (
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    artist_id UUID REFERENCES artists(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'main' CHECK (role IN ('main', 'featured', 'producer')),
    is_primary BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (track_id, artist_id)
);

-- 5. Audio Features Dimension Table (1:1 with Track)
CREATE TABLE IF NOT EXISTS audio_features (
    track_id UUID PRIMARY KEY REFERENCES tracks(id) ON DELETE CASCADE,
    danceability NUMERIC(4,3) CHECK (danceability BETWEEN 0 AND 1),
    energy NUMERIC(4,3) CHECK (energy BETWEEN 0 AND 1),
    key INTEGER CHECK (key BETWEEN -1 AND 11),
    loudness NUMERIC(5,2),
    mode INTEGER CHECK (mode IN (0, 1)),
    speechiness NUMERIC(4,3) CHECK (speechiness BETWEEN 0 AND 1),
    acousticness NUMERIC(4,3) CHECK (acousticness BETWEEN 0 AND 1),
    instrumentalness NUMERIC(4,3) CHECK (instrumentalness BETWEEN 0 AND 1),
    liveness NUMERIC(4,3) CHECK (liveness BETWEEN 0 AND 1),
    valence NUMERIC(4,3) CHECK (valence BETWEEN 0 AND 1),
    tempo NUMERIC(6,2) CHECK (tempo > 0),
    time_signature INTEGER CHECK (time_signature BETWEEN 3 AND 7)
);

-- 6. Track Metrics Fact Table (Decouples popularity score from actual streams)
CREATE TABLE IF NOT EXISTS track_metrics (
    track_id UUID PRIMARY KEY REFERENCES tracks(id) ON DELETE CASCADE,
    popularity INTEGER CHECK (popularity BETWEEN 0 AND 100),
    streams BIGINT CHECK (streams >= 0),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Indexes for High-Performance Queries
CREATE INDEX IF NOT EXISTS idx_tracks_album_id ON tracks(album_id);
CREATE INDEX IF NOT EXISTS idx_track_artists_artist_id ON track_artists(artist_id);
CREATE INDEX IF NOT EXISTS idx_track_artists_is_primary ON track_artists(is_primary);
CREATE INDEX IF NOT EXISTS idx_albums_release_date ON albums(release_date);
CREATE INDEX IF NOT EXISTS idx_track_metrics_streams ON track_metrics(streams DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_track_metrics_popularity ON track_metrics(popularity DESC);
CREATE INDEX IF NOT EXISTS idx_audio_features_dance_energy ON audio_features(danceability, energy);
