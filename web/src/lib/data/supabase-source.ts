import { createClient, SupabaseClient } from "@supabase/supabase-js";
import {
  Track,
  Artist,
  Album,
  TrackDetail,
  ArtistDetail,
  AlbumDetail,
  SearchResults,
  OverviewStats,
} from "./types";
import { getFallbackCover } from "../utils/colors";

let supabaseClient: SupabaseClient | null = null;
let connectionTested = false;
let isConnected = false;

export function isSupabaseConfigured(): boolean {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  return Boolean(
    url &&
      anonKey &&
      !url.includes("your-project-id") &&
      !url.includes("placeholder") &&
      !anonKey.includes("placeholder")
  );
}

function getClient(): SupabaseClient | null {
  if (supabaseClient) return supabaseClient;
  if (!isSupabaseConfigured()) return null;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

  supabaseClient = createClient(url, key, {
    auth: { persistSession: false },
  });
  return supabaseClient;
}

export const supabaseSource = {
  async testConnection(): Promise<boolean> {
    if (connectionTested) return isConnected;
    const client = getClient();
    if (!client) {
      connectionTested = true;
      isConnected = false;
      return false;
    }
    try {
      const { data, error } = await client.from("tracks").select("id").limit(1);
      connectionTested = true;
      isConnected = !error && Boolean(data);
      return isConnected;
    } catch {
      connectionTested = true;
      isConnected = false;
      return false;
    }
  },

  async getTracks(options?: {
    limit?: number;
    genre?: string;
    sort?: "popularity" | "streams" | "title" | "duration";
  }): Promise<Track[]> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    let query = client.from("v_track_analytics").select("*");

    if (options?.genre) {
      query = query.contains("primary_artist_genres", [options.genre]);
    }

    if (options?.sort === "popularity") {
      query = query.order("popularity", { ascending: false });
    } else if (options?.sort === "streams") {
      query = query.order("streams", { ascending: false });
    } else if (options?.sort === "title") {
      query = query.order("track_title", { ascending: true });
    } else if (options?.sort === "duration") {
      query = query.order("duration_ms", { ascending: false });
    }

    if (options?.limit) {
      query = query.limit(options.limit);
    }

    const { data, error } = await query;
    if (error) throw error;

    return (data || []).map((row: any) => ({
      id: row.track_id,
      spotify_track_id: row.spotify_track_id,
      isrc: null,
      title: row.track_title,
      album_id: row.album_id,
      duration_ms: row.duration_ms,
      explicit: Boolean(row.explicit),
      preview_url: row.preview_url,
      album_title: row.album_title,
      cover_image_url: row.cover_image_url || getFallbackCover(row.track_title, "track"),
      artist_name: row.primary_artist_name,
      artist_id: row.primary_artist_id,
      popularity: row.popularity || 0,
      streams: row.streams || 0,
      genres: row.primary_artist_genres || [],
    }));
  },

  async getTrackById(id: string): Promise<TrackDetail | null> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    const { data: trackRow, error: trackErr } = await client
      .from("v_track_analytics")
      .select("*")
      .eq("track_id", id)
      .single();

    if (trackErr || !trackRow) return null;

    const audio_features = {
      track_id: trackRow.track_id,
      danceability: Number(trackRow.danceability) || 0,
      energy: Number(trackRow.energy) || 0,
      key: Number(trackRow.key) || 0,
      loudness: Number(trackRow.loudness) || 0,
      mode: Number(trackRow.mode) || 0,
      speechiness: Number(trackRow.speechiness) || 0,
      acousticness: Number(trackRow.acousticness) || 0,
      instrumentalness: Number(trackRow.instrumentalness) || 0,
      liveness: Number(trackRow.liveness) || 0,
      valence: Number(trackRow.valence) || 0,
      tempo: Number(trackRow.tempo) || 0,
      time_signature: Number(trackRow.time_signature) || 4,
    };

    return {
      id: trackRow.track_id,
      spotify_track_id: trackRow.spotify_track_id,
      isrc: null,
      title: trackRow.track_title,
      album_id: trackRow.album_id,
      duration_ms: trackRow.duration_ms,
      explicit: Boolean(trackRow.explicit),
      preview_url: trackRow.preview_url,
      album_title: trackRow.album_title,
      cover_image_url: trackRow.cover_image_url || getFallbackCover(trackRow.track_title, "track"),
      artist_name: trackRow.primary_artist_name,
      artist_id: trackRow.primary_artist_id,
      popularity: trackRow.popularity || 0,
      streams: trackRow.streams || 0,
      genres: trackRow.primary_artist_genres || [],
      audio_features,
    };
  },

  async getArtists(options?: {
    limit?: number;
    sort?: "popularity" | "streams" | "name";
  }): Promise<Artist[]> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    let query = client.from("v_artist_rankings").select("*");

    if (options?.sort === "popularity") {
      query = query.order("avg_track_popularity", { ascending: false });
    } else if (options?.sort === "streams") {
      query = query.order("total_streams", { ascending: false });
    } else if (options?.sort === "name") {
      query = query.order("artist_name", { ascending: true });
    }

    if (options?.limit) {
      query = query.limit(options.limit);
    }

    const { data, error } = await query;
    if (error) throw error;

    return (data || []).map((row: any) => ({
      id: row.artist_id,
      spotify_artist_id: row.artist_id,
      name: row.artist_name,
      genres: row.genres || [],
      popularity: Math.round(Number(row.avg_track_popularity) || 0),
      image_url: row.image_url || getFallbackCover(row.artist_name, "artist"),
      total_streams: Number(row.total_streams) || 0,
      track_count: Number(row.track_count) || 0,
    }));
  },

  async getArtistById(id: string): Promise<ArtistDetail | null> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    const { data: artistRow, error } = await client
      .from("v_artist_rankings")
      .select("*")
      .eq("artist_id", id)
      .single();

    if (error || !artistRow) return null;

    const { data: topTracks } = await client
      .from("v_track_analytics")
      .select("*")
      .eq("primary_artist_id", id)
      .order("streams", { ascending: false })
      .limit(10);

    const { data: albums } = await client
      .from("albums")
      .select("*")
      .eq("artist_id", id);

    return {
      id: artistRow.artist_id,
      spotify_artist_id: artistRow.artist_id,
      name: artistRow.artist_name,
      genres: artistRow.genres || [],
      popularity: Math.round(Number(artistRow.avg_track_popularity) || 0),
      image_url: artistRow.image_url || getFallbackCover(artistRow.artist_name, "artist"),
      total_streams: Number(artistRow.total_streams) || 0,
      track_count: Number(artistRow.track_count) || 0,
      top_tracks: (topTracks || []).map((r: any) => ({
        id: r.track_id,
        spotify_track_id: r.spotify_track_id,
        isrc: null,
        title: r.track_title,
        album_id: r.album_id,
        duration_ms: r.duration_ms,
        explicit: Boolean(r.explicit),
        preview_url: r.preview_url,
        album_title: r.album_title,
        cover_image_url: r.cover_image_url || getFallbackCover(r.track_title, "track"),
        artist_name: artistRow.artist_name,
        artist_id: id,
        popularity: r.popularity || 0,
        streams: r.streams || 0,
        genres: r.primary_artist_genres || [],
      })),
      albums: (albums || []).map((a: any) => ({
        id: a.id,
        spotify_album_id: a.spotify_album_id,
        title: a.title,
        artist_id: id,
        artist_name: artistRow.artist_name,
        release_date: a.release_date,
        release_date_precision: a.release_date_precision,
        total_tracks: a.total_tracks,
        cover_image_url: a.cover_image_url || getFallbackCover(a.title, "album"),
        genres: artistRow.genres || [],
      })),
    };
  },

  async getAlbums(options?: {
    limit?: number;
    sort?: "release_date" | "title";
  }): Promise<Album[]> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    let query = client.from("albums").select("*, artists(name)");

    if (options?.sort === "release_date") {
      query = query.order("release_date", { ascending: false });
    } else if (options?.sort === "title") {
      query = query.order("title", { ascending: true });
    }

    if (options?.limit) {
      query = query.limit(options.limit);
    }

    const { data, error } = await query;
    if (error) throw error;

    return (data || []).map((row: any) => ({
      id: row.id,
      spotify_album_id: row.spotify_album_id,
      title: row.title,
      artist_id: row.artist_id,
      artist_name: row.artists?.name || "Unknown Artist",
      release_date: row.release_date,
      release_date_precision: row.release_date_precision,
      total_tracks: row.total_tracks,
      cover_image_url: row.cover_image_url || getFallbackCover(row.title, "album"),
      genres: [],
    }));
  },

  async getAlbumById(id: string): Promise<AlbumDetail | null> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    const { data: albumRow, error } = await client
      .from("albums")
      .select("*, artists(name)")
      .eq("id", id)
      .single();

    if (error || !albumRow) return null;

    const { data: tracks } = await client
      .from("v_track_analytics")
      .select("*")
      .eq("album_id", id);

    return {
      id: albumRow.id,
      spotify_album_id: albumRow.spotify_album_id,
      title: albumRow.title,
      artist_id: albumRow.artist_id,
      artist_name: albumRow.artists?.name || "Unknown Artist",
      release_date: albumRow.release_date,
      release_date_precision: albumRow.release_date_precision,
      total_tracks: albumRow.total_tracks,
      cover_image_url: albumRow.cover_image_url || getFallbackCover(albumRow.title, "album"),
      tracks: (tracks || []).map((r: any) => ({
        id: r.track_id,
        spotify_track_id: r.spotify_track_id,
        isrc: null,
        title: r.track_title,
        album_id: id,
        duration_ms: r.duration_ms,
        explicit: Boolean(r.explicit),
        preview_url: r.preview_url,
        album_title: albumRow.title,
        cover_image_url: albumRow.cover_image_url || getFallbackCover(r.track_title, "track"),
        artist_name: albumRow.artists?.name || "Unknown Artist",
        artist_id: albumRow.artist_id,
        popularity: r.popularity || 0,
        streams: r.streams || 0,
        genres: [],
      })),
    };
  },

  async searchAll(query: string): Promise<SearchResults> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    const q = `%${query.trim()}%`;
    const [tRes, aRes, alRes] = await Promise.all([
      client.from("v_track_analytics").select("*").ilike("track_title", q).limit(15),
      client.from("v_artist_rankings").select("*").ilike("artist_name", q).limit(10),
      client.from("albums").select("*, artists(name)").ilike("title", q).limit(10),
    ]);

    const tracks: Track[] = (tRes.data || []).map((r: any) => ({
      id: r.track_id,
      spotify_track_id: r.spotify_track_id,
      isrc: null,
      title: r.track_title,
      album_id: r.album_id,
      duration_ms: r.duration_ms,
      explicit: Boolean(r.explicit),
      preview_url: r.preview_url,
      album_title: r.album_title,
      cover_image_url: r.cover_image_url || getFallbackCover(r.track_title, "track"),
      artist_name: r.primary_artist_name,
      artist_id: r.primary_artist_id,
      popularity: r.popularity || 0,
      streams: r.streams || 0,
      genres: r.primary_artist_genres || [],
    }));

    const artists: Artist[] = (aRes.data || []).map((r: any) => ({
      id: r.artist_id,
      spotify_artist_id: r.artist_id,
      name: r.artist_name,
      genres: r.genres || [],
      popularity: Math.round(Number(r.avg_track_popularity) || 0),
      image_url: r.image_url || getFallbackCover(r.artist_name, "artist"),
      total_streams: Number(r.total_streams) || 0,
      track_count: Number(r.track_count) || 0,
    }));

    const albums: Album[] = (alRes.data || []).map((r: any) => ({
      id: r.id,
      spotify_album_id: r.spotify_album_id,
      title: r.title,
      artist_id: r.artist_id,
      artist_name: r.artists?.name || "Unknown Artist",
      release_date: r.release_date,
      release_date_precision: r.release_date_precision,
      total_tracks: r.total_tracks,
      cover_image_url: r.cover_image_url || getFallbackCover(r.title, "album"),
      genres: [],
    }));

    return {
      query,
      tracks,
      artists,
      albums,
      genres: [],
    };
  },

  async getOverviewStats(): Promise<OverviewStats> {
    const client = getClient();
    if (!client) throw new Error("Supabase not configured");

    const [tCount, aCount, alCount] = await Promise.all([
      client.from("tracks").select("id", { count: "exact", head: true }),
      client.from("artists").select("id", { count: "exact", head: true }),
      client.from("albums").select("id", { count: "exact", head: true }),
    ]);

    return {
      total_tracks: tCount.count || 0,
      total_artists: aCount.count || 0,
      total_albums: alCount.count || 0,
      total_streams: 0,
      top_genre: "Electronic",
    };
  },
};
