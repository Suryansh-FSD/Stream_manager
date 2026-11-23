export interface AudioFeatures {
  track_id: string;
  danceability: number;
  energy: number;
  key: number;
  loudness: number;
  mode: number;
  speechiness: number;
  acousticness: number;
  instrumentalness: number;
  liveness: number;
  valence: number;
  tempo: number;
  time_signature: number;
}

export interface TrackMetrics {
  track_id: string;
  popularity: number;
  streams: number;
}

export interface ArtistRef {
  id: string;
  name: string;
  role?: string;
  is_primary?: boolean;
}

export interface Track {
  id: string;
  spotify_track_id: string | null;
  isrc: string | null;
  title: string;
  album_id: string | null;
  duration_ms: number;
  explicit: boolean;
  preview_url: string | null;

  // Joined metadata
  album_title?: string;
  cover_image_url?: string;
  artist_name?: string;
  artist_id?: string;
  artists?: ArtistRef[];
  popularity?: number;
  streams?: number;
  genres?: string[];
  audio_features?: AudioFeatures;
}

export interface Artist {
  id: string;
  spotify_artist_id: string | null;
  name: string;
  genres: string[];
  popularity: number;
  image_url: string | null;
  total_streams?: number;
  track_count?: number;
}

export interface Album {
  id: string;
  spotify_album_id: string | null;
  title: string;
  artist_id: string | null;
  artist_name?: string;
  release_date: string | null;
  release_date_precision: string | null;
  total_tracks: number;
  cover_image_url: string | null;
  genres?: string[];
}

export interface TrackDetail extends Track {
  audio_features?: AudioFeatures;
  album?: Album;
  all_artists?: Artist[];
}

export interface ArtistDetail extends Artist {
  top_tracks: Track[];
  albums: Album[];
  related_artists?: Artist[];
}

export interface AlbumDetail extends Album {
  tracks: Track[];
  artist?: Artist;
}

export interface SearchResults {
  query: string;
  tracks: Track[];
  artists: Artist[];
  albums: Album[];
  genres: string[];
}

export interface OverviewStats {
  total_tracks: number;
  total_artists: number;
  total_albums: number;
  total_streams: number;
  top_genre: string;
}
