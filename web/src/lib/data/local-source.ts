import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";
import {
  Track,
  Artist,
  Album,
  AudioFeatures,
  TrackMetrics,
  TrackDetail,
  ArtistDetail,
  AlbumDetail,
  SearchResults,
  OverviewStats,
  ArtistRef,
} from "./types";
import { getFallbackCover } from "../utils/colors";

interface ParsedDatabase {
  tracks: Track[];
  artists: Artist[];
  albums: Album[];
  audioFeatures: Map<string, AudioFeatures>;
  trackMetrics: Map<string, TrackMetrics>;
  tracksById: Map<string, Track>;
  artistsById: Map<string, Artist>;
  albumsById: Map<string, Album>;
  tracksByAlbumId: Map<string, Track[]>;
  tracksByArtistId: Map<string, Track[]>;
}

let cachedDb: ParsedDatabase | null = null;

function resolveDataDir(): string {
  const candidateDirs = [
    path.resolve(process.cwd(), "data/processed"),
    path.resolve(process.cwd(), "../data/processed"),
    path.resolve(__dirname, "../../../../../data/processed"),
    path.resolve(__dirname, "../../../../data/processed"),
  ];

  for (const dir of candidateDirs) {
    if (fs.existsSync(dir) && fs.existsSync(path.join(dir, "tracks.csv"))) {
      return dir;
    }
  }
  return candidateDirs[0];
}

function parseGenres(genresStr: string | undefined): string[] {
  if (!genresStr) return [];
  const trimmed = genresStr.trim();
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
    try {
      const jsonStr = trimmed.replace(/'/g, '"');
      return JSON.parse(jsonStr);
    } catch {
      return trimmed
        .slice(1, -1)
        .split(",")
        .map((s) => s.trim().replace(/^['"]|['"]$/g, ""))
        .filter(Boolean);
    }
  }
  return trimmed
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);
}

function loadDatabase(): ParsedDatabase {
  if (cachedDb) return cachedDb;

  const dataDir = resolveDataDir();

  // Read raw CSV strings
  const readCsv = (filename: string): any[] => {
    const fullPath = path.join(dataDir, filename);
    if (!fs.existsSync(fullPath)) return [];
    const content = fs.readFileSync(fullPath, "utf-8");
    return parse(content, { columns: true, skip_empty_lines: true, trim: true });
  };

  const rawArtists = readCsv("artists.csv");
  const rawAlbums = readCsv("albums.csv");
  const rawTracks = readCsv("tracks.csv");
  const rawTrackArtists = readCsv("track_artists.csv");
  const rawAudioFeatures = readCsv("audio_features.csv");
  const rawMetrics = readCsv("track_metrics.csv");

  // Index audio features
  const audioFeatures = new Map<string, AudioFeatures>();
  for (const r of rawAudioFeatures) {
    audioFeatures.set(r.track_id, {
      track_id: r.track_id,
      danceability: parseFloat(r.danceability) || 0,
      energy: parseFloat(r.energy) || 0,
      key: parseInt(r.key) || 0,
      loudness: parseFloat(r.loudness) || 0,
      mode: parseInt(r.mode) || 0,
      speechiness: parseFloat(r.speechiness) || 0,
      acousticness: parseFloat(r.acousticness) || 0,
      instrumentalness: parseFloat(r.instrumentalness) || 0,
      liveness: parseFloat(r.liveness) || 0,
      valence: parseFloat(r.valence) || 0,
      tempo: parseFloat(r.tempo) || 0,
      time_signature: parseInt(r.time_signature) || 4,
    });
  }

  // Index track metrics
  const trackMetrics = new Map<string, TrackMetrics>();
  for (const r of rawMetrics) {
    trackMetrics.set(r.track_id, {
      track_id: r.track_id,
      popularity: parseInt(r.popularity) || 0,
      streams: parseInt(r.streams) || 0,
    });
  }

  // Index track artist associations: track_id -> ArtistRef[]
  const trackArtistsMap = new Map<string, { artist_id: string; role: string; is_primary: boolean }[]>();
  for (const r of rawTrackArtists) {
    const list = trackArtistsMap.get(r.track_id) || [];
    list.push({
      artist_id: r.artist_id,
      role: r.role || "main",
      is_primary: String(r.is_primary).toLowerCase() === "true" || r.is_primary === "1",
    });
    trackArtistsMap.set(r.track_id, list);
  }

  // Parse artists
  const artistsById = new Map<string, Artist>();
  const artists: Artist[] = rawArtists.map((r) => {
    const parsedGenres = parseGenres(r.genres);
    const artist: Artist = {
      id: r.id,
      spotify_artist_id: r.spotify_artist_id || r.id,
      name: r.name,
      genres: parsedGenres,
      popularity: parseInt(r.popularity) || 0,
      image_url: r.image_url || getFallbackCover(r.name, "artist"),
      total_streams: 0,
      track_count: 0,
    };
    artistsById.set(artist.id, artist);
    return artist;
  });

  // Parse albums
  const albumsById = new Map<string, Album>();
  const albums: Album[] = rawAlbums.map((r) => {
    const artist = artistsById.get(r.artist_id);
    const album: Album = {
      id: r.id,
      spotify_album_id: r.spotify_album_id || r.id,
      title: r.title,
      artist_id: r.artist_id || null,
      artist_name: artist ? artist.name : undefined,
      release_date: r.release_date || null,
      release_date_precision: r.release_date_precision || "day",
      total_tracks: parseInt(r.total_tracks) || 1,
      cover_image_url: r.cover_image_url || getFallbackCover(r.title, "album"),
      genres: artist ? artist.genres : [],
    };
    albumsById.set(album.id, album);
    return album;
  });

  // Parse tracks & enrich
  const tracksById = new Map<string, Track>();
  const tracksByAlbumId = new Map<string, Track[]>();
  const tracksByArtistId = new Map<string, Track[]>();

  const tracks: Track[] = rawTracks.map((r) => {
    const album = albumsById.get(r.album_id);
    const artistLinks = trackArtistsMap.get(r.id) || [];

    const artistRefs: ArtistRef[] = artistLinks.map((al) => {
      const art = artistsById.get(al.artist_id);
      return {
        id: al.artist_id,
        name: art ? art.name : "Unknown Artist",
        role: al.role,
        is_primary: al.is_primary,
      };
    });

    const primaryRef = artistRefs.find((a) => a.is_primary) || artistRefs[0];
    const metric = trackMetrics.get(r.id);
    const features = audioFeatures.get(r.id);

    const primaryArtist = primaryRef ? artistsById.get(primaryRef.id) : null;
    const genres = primaryArtist ? primaryArtist.genres : album?.genres || [];

    const track: Track = {
      id: r.id,
      spotify_track_id: r.spotify_track_id || r.id,
      isrc: r.isrc || null,
      title: r.title,
      album_id: r.album_id || null,
      duration_ms: parseInt(r.duration_ms) || 0,
      explicit: String(r.explicit).toLowerCase() === "true" || r.explicit === "1",
      preview_url: r.preview_url || null,
      album_title: album?.title || "Single",
      cover_image_url: album?.cover_image_url || getFallbackCover(r.title, "track"),
      artist_name: primaryRef ? primaryRef.name : (album?.artist_name || "Unknown Artist"),
      artist_id: primaryRef ? primaryRef.id : album?.artist_id || undefined,
      artists: artistRefs,
      popularity: metric ? metric.popularity : 0,
      streams: metric ? metric.streams : 0,
      genres,
      audio_features: features,
    };

    tracksById.set(track.id, track);

    // Group by album
    if (track.album_id) {
      const aList = tracksByAlbumId.get(track.album_id) || [];
      aList.push(track);
      tracksByAlbumId.set(track.album_id, aList);
    }

    // Group by artists
    for (const aRef of artistRefs) {
      const artList = tracksByArtistId.get(aRef.id) || [];
      artList.push(track);
      tracksByArtistId.set(aRef.id, artList);

      // Accumulate streams for primary artist
      if (aRef.is_primary && metric) {
        const art = artistsById.get(aRef.id);
        if (art) {
          art.total_streams = (art.total_streams || 0) + metric.streams;
          art.track_count = (art.track_count || 0) + 1;
        }
      }
    }

    return track;
  });

  cachedDb = {
    tracks,
    artists,
    albums,
    audioFeatures,
    trackMetrics,
    tracksById,
    artistsById,
    albumsById,
    tracksByAlbumId,
    tracksByArtistId,
  };

  return cachedDb;
}

export const localSource = {
  async getTracks(options?: {
    limit?: number;
    genre?: string;
    sort?: "popularity" | "streams" | "title" | "duration";
  }): Promise<Track[]> {
    const db = loadDatabase();
    let result = [...db.tracks];

    if (options?.genre) {
      const gLower = options.genre.toLowerCase();
      result = result.filter((t) => t.genres?.some((g) => g.toLowerCase() === gLower));
    }

    if (options?.sort === "popularity") {
      result.sort((a, b) => (b.popularity || 0) - (a.popularity || 0));
    } else if (options?.sort === "streams") {
      result.sort((a, b) => (b.streams || 0) - (a.streams || 0));
    } else if (options?.sort === "title") {
      result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (options?.sort === "duration") {
      result.sort((a, b) => b.duration_ms - a.duration_ms);
    }

    if (options?.limit && options.limit > 0) {
      result = result.slice(0, options.limit);
    }

    return result;
  },

  async getTrackById(id: string): Promise<TrackDetail | null> {
    const db = loadDatabase();
    const track = db.tracksById.get(id);
    if (!track) return null;

    const album = track.album_id ? db.albumsById.get(track.album_id) : undefined;
    const all_artists = (track.artists || [])
      .map((a) => db.artistsById.get(a.id))
      .filter((a): a is Artist => Boolean(a));

    return {
      ...track,
      album,
      all_artists,
      audio_features: db.audioFeatures.get(track.id),
    };
  },

  async getArtists(options?: {
    limit?: number;
    sort?: "popularity" | "streams" | "name";
  }): Promise<Artist[]> {
    const db = loadDatabase();
    let result = [...db.artists];

    if (options?.sort === "popularity") {
      result.sort((a, b) => (b.popularity || 0) - (a.popularity || 0));
    } else if (options?.sort === "streams") {
      result.sort((a, b) => (b.total_streams || 0) - (a.total_streams || 0));
    } else if (options?.sort === "name") {
      result.sort((a, b) => a.name.localeCompare(b.name));
    }

    if (options?.limit && options.limit > 0) {
      result = result.slice(0, options.limit);
    }

    return result;
  },

  async getArtistById(id: string): Promise<ArtistDetail | null> {
    const db = loadDatabase();
    const artist = db.artistsById.get(id);
    if (!artist) return null;

    const artistTracks = db.tracksByArtistId.get(id) || [];
    const topTracks = [...artistTracks]
      .sort((a, b) => (b.streams || 0) - (a.streams || 0))
      .slice(0, 10);

    const albums = db.albums.filter((a) => a.artist_id === id);

    return {
      ...artist,
      top_tracks: topTracks,
      albums,
    };
  },

  async getAlbums(options?: {
    limit?: number;
    sort?: "release_date" | "title";
  }): Promise<Album[]> {
    const db = loadDatabase();
    let result = [...db.albums];

    if (options?.sort === "release_date") {
      result.sort((a, b) => (b.release_date || "").localeCompare(a.release_date || ""));
    } else if (options?.sort === "title") {
      result.sort((a, b) => a.title.localeCompare(b.title));
    }

    if (options?.limit && options.limit > 0) {
      result = result.slice(0, options.limit);
    }

    return result;
  },

  async getAlbumById(id: string): Promise<AlbumDetail | null> {
    const db = loadDatabase();
    const album = db.albumsById.get(id);
    if (!album) return null;

    const tracks = db.tracksByAlbumId.get(id) || [];
    const artist = album.artist_id ? db.artistsById.get(album.artist_id) : undefined;

    return {
      ...album,
      tracks,
      artist,
    };
  },

  async searchAll(query: string): Promise<SearchResults> {
    const db = loadDatabase();
    const q = query.trim().toLowerCase();

    if (!q) {
      return { query, tracks: [], artists: [], albums: [], genres: [] };
    }

    const tracks = db.tracks
      .filter((t) => t.title.toLowerCase().includes(q) || t.artist_name?.toLowerCase().includes(q))
      .slice(0, 20);

    const artists = db.artists
      .filter((a) => a.name.toLowerCase().includes(q))
      .slice(0, 10);

    const albums = db.albums
      .filter((al) => al.title.toLowerCase().includes(q) || al.artist_name?.toLowerCase().includes(q))
      .slice(0, 10);

    // Matching genres
    const genreSet = new Set<string>();
    for (const a of db.artists) {
      for (const g of a.genres) {
        if (g.toLowerCase().includes(q)) {
          genreSet.add(g);
        }
      }
    }

    return {
      query,
      tracks,
      artists,
      albums,
      genres: Array.from(genreSet).slice(0, 8),
    };
  },

  async getOverviewStats(): Promise<OverviewStats> {
    const db = loadDatabase();
    let totalStreams = 0;
    const genreCounts = new Map<string, number>();

    for (const t of db.tracks) {
      totalStreams += t.streams || 0;
      for (const g of t.genres || []) {
        genreCounts.set(g, (genreCounts.get(g) || 0) + 1);
      }
    }

    let topGenre = "Electronic";
    let maxCount = 0;
    for (const [g, count] of genreCounts.entries()) {
      if (count > maxCount) {
        maxCount = count;
        topGenre = g;
      }
    }

    return {
      total_tracks: db.tracks.length,
      total_artists: db.artists.length,
      total_albums: db.albums.length,
      total_streams: totalStreams,
      top_genre: topGenre,
    };
  },
};
