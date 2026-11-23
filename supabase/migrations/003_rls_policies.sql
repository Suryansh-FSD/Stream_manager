-- ==============================================================================
-- Migration 003: Row Level Security (RLS) Policies
-- ==============================================================================

-- Enable RLS on all base tables
ALTER TABLE artists ENABLE ROW LEVEL SECURITY;
ALTER TABLE albums ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE track_artists ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE track_metrics ENABLE ROW LEVEL SECURITY;

-- 1. Public Read-Only Access (Anon Key)
-- Allows the Next.js client, server components, and Streamlit app to read data
CREATE POLICY "Public Read Access Artists" ON artists FOR SELECT USING (true);
CREATE POLICY "Public Read Access Albums" ON albums FOR SELECT USING (true);
CREATE POLICY "Public Read Access Tracks" ON tracks FOR SELECT USING (true);
CREATE POLICY "Public Read Access Track Artists" ON track_artists FOR SELECT USING (true);
CREATE POLICY "Public Read Access Audio Features" ON audio_features FOR SELECT USING (true);
CREATE POLICY "Public Read Access Track Metrics" ON track_metrics FOR SELECT USING (true);

-- 2. Restrict Insert/Update/Delete to Service Role
-- The service role bypasses RLS by default in Supabase. These explicit policies ensure
-- non-service accounts cannot mutate core catalogue data.
CREATE POLICY "Service Role Full Access Artists" ON artists FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service Role Full Access Albums" ON albums FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service Role Full Access Tracks" ON tracks FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service Role Full Access Track Artists" ON track_artists FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service Role Full Access Audio Features" ON audio_features FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service Role Full Access Track Metrics" ON track_metrics FOR ALL USING (auth.role() = 'service_role');
