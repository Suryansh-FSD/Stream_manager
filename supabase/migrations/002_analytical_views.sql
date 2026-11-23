-- ==============================================================================
-- Migration 002: Analytical Views for Next.js and Streamlit Studio
-- ==============================================================================

-- 1. Comprehensive View: Track Analytics & Audio Profile
CREATE OR REPLACE VIEW v_track_analytics AS
SELECT 
    t.id AS track_id,
    t.spotify_track_id,
    t.title AS track_title,
    t.duration_ms,
    t.explicit,
    t.preview_url,
    a.id AS album_id,
    a.title AS album_title,
    a.release_date,
    a.cover_image_url,
    art.id AS primary_artist_id,
    art.name AS primary_artist_name,
    art.genres AS primary_artist_genres,
    tm.popularity,
    tm.streams,
    af.danceability,
    af.energy,
    af.key,
    af.loudness,
    af.mode,
    af.speechiness,
    af.acousticness,
    af.instrumentalness,
    af.liveness,
    af.valence,
    af.tempo,
    af.time_signature
FROM tracks t
LEFT JOIN albums a ON t.album_id = a.id
LEFT JOIN track_artists ta ON t.id = ta.track_id AND ta.is_primary = TRUE
LEFT JOIN artists art ON ta.artist_id = art.id
LEFT JOIN track_metrics tm ON t.id = tm.track_id
LEFT JOIN audio_features af ON t.id = af.track_id;

-- 2. Artist Rankings: Aggregating tracks & streams safely without duplication
CREATE OR REPLACE VIEW v_artist_rankings AS
SELECT 
    art.id AS artist_id,
    art.name AS artist_name,
    art.genres,
    art.image_url,
    COUNT(DISTINCT t.id) AS track_count,
    COALESCE(SUM(tm.streams), 0) AS total_streams,
    ROUND(AVG(tm.popularity), 1) AS avg_track_popularity,
    ROUND(AVG(af.danceability), 3) AS avg_danceability,
    ROUND(AVG(af.energy), 3) AS avg_energy,
    ROUND(AVG(af.valence), 3) AS avg_valence
FROM artists art
JOIN track_artists ta ON art.id = ta.artist_id AND ta.is_primary = TRUE
JOIN tracks t ON ta.track_id = t.id
LEFT JOIN track_metrics tm ON t.id = tm.track_id
LEFT JOIN audio_features af ON t.id = af.track_id
GROUP BY art.id, art.name, art.genres, art.image_url;

-- 3. Genre Intelligence View: Unnesting genres with performance statistics
CREATE OR REPLACE VIEW v_genre_metrics AS
SELECT 
    genre,
    COUNT(DISTINCT t.id) AS track_count,
    COUNT(DISTINCT art.id) AS artist_count,
    COALESCE(SUM(tm.streams), 0) AS total_streams,
    ROUND(AVG(tm.popularity), 1) AS avg_popularity,
    ROUND(AVG(af.danceability), 3) AS avg_danceability,
    ROUND(AVG(af.energy), 3) AS avg_energy,
    ROUND(AVG(af.valence), 3) AS avg_valence,
    ROUND(AVG(af.tempo), 1) AS avg_tempo
FROM artists art,
UNNEST(art.genres) AS genre
JOIN track_artists ta ON art.id = ta.artist_id AND ta.is_primary = TRUE
JOIN tracks t ON ta.track_id = t.id
LEFT JOIN track_metrics tm ON t.id = tm.track_id
LEFT JOIN audio_features af ON t.id = af.track_id
GROUP BY genre;

-- 4. Yearly Music Trends View
CREATE OR REPLACE VIEW v_yearly_music_trends AS
SELECT 
    EXTRACT(YEAR FROM a.release_date)::INTEGER AS release_year,
    COUNT(DISTINCT t.id) AS track_count,
    COUNT(DISTINCT art.id) AS active_artists_count,
    COALESCE(SUM(tm.streams), 0) AS total_streams,
    ROUND(AVG(tm.popularity), 1) AS avg_popularity,
    ROUND(AVG(af.danceability), 3) AS avg_danceability,
    ROUND(AVG(af.energy), 3) AS avg_energy,
    ROUND(AVG(af.valence), 3) AS avg_valence,
    ROUND(AVG(af.acousticness), 3) AS avg_acousticness,
    ROUND(AVG(af.tempo), 1) AS avg_tempo
FROM tracks t
JOIN albums a ON t.album_id = a.id
JOIN track_artists ta ON t.id = ta.track_id AND ta.is_primary = TRUE
JOIN artists art ON ta.artist_id = art.id
LEFT JOIN track_metrics tm ON t.id = tm.track_id
LEFT JOIN audio_features af ON t.id = af.track_id
WHERE a.release_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM a.release_date)
ORDER BY release_year DESC;
