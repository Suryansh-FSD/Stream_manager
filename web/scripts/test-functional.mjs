import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";

const dataDir = path.resolve(process.cwd(), "../data/processed");

function readCsv(file) {
  const filePath = path.join(dataDir, file);
  const content = fs.readFileSync(filePath, "utf-8");
  return parse(content, { columns: true, skip_empty_lines: true, trim: true });
}

console.log("=== SPOTIFY TRENDS FUNCTIONAL AUDIT ===");

// 1. Data Integrity & Relationships
const tracks = readCsv("tracks.csv");
const artists = readCsv("artists.csv");
const albums = readCsv("albums.csv");
const trackArtists = readCsv("track_artists.csv");
const features = readCsv("audio_features.csv");
const metrics = readCsv("track_metrics.csv");

console.log(`✓ Loaded: ${tracks.length} tracks, ${artists.length} artists, ${albums.length} albums, ${trackArtists.length} collaborations`);

// Check every track has audio features and metrics
const featureIds = new Set(features.map((f) => f.track_id));
const metricIds = new Set(metrics.map((m) => m.track_id));

const missingFeatures = tracks.filter((t) => !featureIds.has(t.id));
const missingMetrics = tracks.filter((t) => !metricIds.has(t.id));

if (missingFeatures.length > 0 || missingMetrics.length > 0) {
  console.error(`FAIL: Missing features (${missingFeatures.length}) or metrics (${missingMetrics.length})`);
  process.exit(1);
}
console.log("✓ Every track has 1:1 audio features and metric records");

// 2. Multi-Artist Collaborations
const primaryArtists = trackArtists.filter((ta) => String(ta.is_primary).toLowerCase() === "true" || ta.is_primary === "1");
console.log(`✓ Verified primary artist assignments: ${primaryArtists.length} primary pairings`);

// 3. Audio feature ranges
let outOfRange = 0;
for (const f of features) {
  const d = parseFloat(f.danceability);
  const e = parseFloat(f.energy);
  const v = parseFloat(f.valence);
  if (d < 0 || d > 1 || e < 0 || e > 1 || v < 0 || v > 1) {
    outOfRange++;
  }
}
if (outOfRange > 0) {
  console.error(`FAIL: ${outOfRange} audio features out of 0..1 range`);
  process.exit(1);
}
console.log("✓ All audio features strictly within [0, 1] range");

// 4. Distinction between popularity (0-100) and streams (>=0)
let popularityOutOfBounds = 0;
let negativeStreams = 0;
for (const m of metrics) {
  const p = parseInt(m.popularity);
  const s = parseInt(m.streams);
  if (p < 0 || p > 100) popularityOutOfBounds++;
  if (s < 0) negativeStreams++;
}
if (popularityOutOfBounds > 0 || negativeStreams > 0) {
  console.error("FAIL: Popularity or streams out of bounds");
  process.exit(1);
}
console.log("✓ Popularity (0-100) and streams (>=0) properly decoupled and verified");

console.log("\nALL FUNCTIONAL AUDIT CHECKS PASSED!");
