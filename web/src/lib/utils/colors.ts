// Deterministic aesthetic gradient and cover artwork generator for albums, artists and genres

const GRADIENT_PALETTES = [
  "from-emerald-500 via-teal-600 to-slate-900",
  "from-purple-600 via-indigo-600 to-slate-900",
  "from-rose-500 via-pink-600 to-purple-950",
  "from-amber-500 via-orange-600 to-stone-900",
  "from-blue-600 via-cyan-600 to-slate-950",
  "from-fuchsia-600 via-pink-700 to-neutral-900",
  "from-teal-500 via-cyan-700 to-blue-950",
  "from-violet-600 via-purple-800 to-neutral-950",
  "from-red-600 via-amber-700 to-zinc-900",
  "from-lime-500 via-emerald-700 to-slate-900",
];

const GENRE_COLORS: Record<string, string> = {
  "Dream Pop": "#8b5cf6",
  "Lo-Fi Beats": "#06b6d4",
  "Deep House": "#3b82f6",
  Ambient: "#10b981",
  "R&B": "#ec4899",
  Electronic: "#6366f1",
  "Indie Pop": "#f59e0b",
  Synthwave: "#f43f5e",
  "Future Bass": "#14b8a6",
  "Alternative Rock": "#ef4444",
  Pop: "#d946ef",
  Rock: "#e11d48",
  Jazz: "#b45309",
  HipHop: "#eab308",
  Classical: "#64748b",
};

export function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function getGradientForId(id: string): string {
  const index = hashString(id) % GRADIENT_PALETTES.length;
  return GRADIENT_PALETTES[index];
}

export function getGenreColor(genre: string): string {
  return GENRE_COLORS[genre] || "#1DB954";
}

export function getFallbackCover(
  title: string,
  type: "album" | "artist" | "track" = "album"
): string {
  // Deterministic SVG data URL with music icon and stylish gradients
  const hash = hashString(title);
  const colorA = `hsl(${hash % 360}, 70%, 45%)`;
  const colorB = `hsl(${(hash + 60) % 360}, 65%, 20%)`;
  const initial = (title || "M").charAt(0).toUpperCase();

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
    <defs>
      <linearGradient id="g_${hash}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${colorA}" />
        <stop offset="100%" stop-color="${colorB}" />
      </linearGradient>
    </defs>
    <rect width="400" height="400" fill="url(#g_${hash})" />
    <circle cx="200" cy="200" r="${type === "artist" ? 120 : 90}" fill="rgba(255,255,255,0.08)" />
    <text x="200" y="225" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="${type === "artist" ? 110 : 80}" font-weight="700" fill="rgba(255,255,255,0.9)" text-anchor="middle" dominant-baseline="middle">${initial}</text>
  </svg>`;

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}
