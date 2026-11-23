import { localSource } from "./local-source";
import { supabaseSource, isSupabaseConfigured } from "./supabase-source";
import {
  Track,
  TrackDetail,
  Artist,
  ArtistDetail,
  Album,
  AlbumDetail,
  SearchResults,
  OverviewStats,
} from "./types";

/**
 * Unified Repository Layer
 * Automatically uses Supabase if credentials are provided and connected.
 * Gracefully defaults to high-performance local normalized files otherwise.
 */
export const repository = {
  async getDataSourceName(): Promise<"supabase" | "local"> {
    if (isSupabaseConfigured()) {
      const live = await supabaseSource.testConnection();
      if (live) return "supabase";
    }
    return "local";
  },

  async getTracks(options?: {
    limit?: number;
    genre?: string;
    sort?: "popularity" | "streams" | "title" | "duration";
  }): Promise<Track[]> {
    if (isSupabaseConfigured()) {
      try {
        return await supabaseSource.getTracks(options);
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getTracks(options);
  },

  async getTrackById(id: string): Promise<TrackDetail | null> {
    if (isSupabaseConfigured()) {
      try {
        const result = await supabaseSource.getTrackById(id);
        if (result) return result;
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getTrackById(id);
  },

  async getArtists(options?: {
    limit?: number;
    sort?: "popularity" | "streams" | "name";
  }): Promise<Artist[]> {
    if (isSupabaseConfigured()) {
      try {
        return await supabaseSource.getArtists(options);
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getArtists(options);
  },

  async getArtistById(id: string): Promise<ArtistDetail | null> {
    if (isSupabaseConfigured()) {
      try {
        const result = await supabaseSource.getArtistById(id);
        if (result) return result;
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getArtistById(id);
  },

  async getAlbums(options?: {
    limit?: number;
    sort?: "release_date" | "title";
  }): Promise<Album[]> {
    if (isSupabaseConfigured()) {
      try {
        return await supabaseSource.getAlbums(options);
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getAlbums(options);
  },

  async getAlbumById(id: string): Promise<AlbumDetail | null> {
    if (isSupabaseConfigured()) {
      try {
        const result = await supabaseSource.getAlbumById(id);
        if (result) return result;
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getAlbumById(id);
  },

  async searchAll(query: string): Promise<SearchResults> {
    if (isSupabaseConfigured()) {
      try {
        return await supabaseSource.searchAll(query);
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.searchAll(query);
  },

  async getOverviewStats(): Promise<OverviewStats> {
    if (isSupabaseConfigured()) {
      try {
        return await supabaseSource.getOverviewStats();
      } catch (err) {
        console.warn("Supabase query failed, falling back to local dataset:", err);
      }
    }
    return localSource.getOverviewStats();
  },
};
