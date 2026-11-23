import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";

const dataDir = path.resolve(process.cwd(), "../data/processed");
console.log(`Checking data directory: ${dataDir}`);

function countCsv(file) {
  const filePath = path.join(dataDir, file);
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, "utf-8");
  const rows = parse(content, { columns: true, skip_empty_lines: true, trim: true });
  return rows.length;
}

const files = [
  { name: "tracks.csv", expected: 495 },
  { name: "artists.csv", expected: 18 },
  { name: "albums.csv", expected: 357 },
  { name: "track_artists.csv", expected: 817 },
  { name: "audio_features.csv", expected: 495 },
  { name: "track_metrics.csv", expected: 495 },
];

let allPassed = true;
for (const f of files) {
  const count = countCsv(f.name);
  const ok = count === f.expected;
  console.log(`- ${f.name}: ${count} rows (expected ${f.expected}) -> ${ok ? "PASS" : "FAIL"}`);
  if (!ok) allPassed = false;
}

if (!allPassed) {
  console.error("Test failed: Row count mismatch!");
  process.exit(1);
} else {
  console.log("All data files validated successfully!");
}
