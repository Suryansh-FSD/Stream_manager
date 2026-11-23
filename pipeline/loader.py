"""
Supabase Database Loader for the Spotify Trends Data Engineering Pipeline.
Handles normalized entity extraction, referential batch upserts,
and local processed data exports.
"""
import os
import uuid
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from pathlib import Path

from pipeline.config import PipelineConfig, PROCESSED_DATA_DIR


class SupabaseLoader:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes Supabase client if credentials are provided in the environment."""
        url = self.config.supabase_url
        key = self.config.supabase_key

        if url and key and "your-project-id" not in url:
            try:
                from supabase import create_client, Client
                self.client: Optional[Client] = create_client(url, key)
            except Exception as e:
                print(f"[SupabaseLoader] Warning: Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            self.client = None

    def is_connected(self) -> bool:
        """Returns True if a live Supabase client connection is active."""
        return self.client is not None

    @staticmethod
    def prepare_relational_tables(
        cleaned_df: pd.DataFrame, 
        track_artists_records: List[Dict[str, Any]]
    ) -> Dict[str, pd.DataFrame]:
        """
        Deconstructs the cleaned DataFrame into the 6 normalized database entities
        matching the Supabase SQL schema migrations:
        1. artists
        2. albums
        3. tracks
        4. track_artists
        5. audio_features
        6. track_metrics
        """
        # 1. Artists Table
        unique_artists = {}
        for ta in track_artists_records:
            art_id = ta["artist_id"]
            if art_id not in unique_artists:
                unique_artists[art_id] = {
                    "id": art_id,
                    "spotify_artist_id": art_id,
                    "name": ta["artist_name"],
                    "genres": []
                }

        # If genre is present in cleaned_df, map it to the primary artist
        if "genre" in cleaned_df.columns:
            for _, row in cleaned_df.iterrows():
                p_art = row["primary_artist"]
                g = str(row["genre"]).strip()
                if g and g.lower() not in ["none", "nan", ""]:
                    for a_data in unique_artists.values():
                        if a_data["name"] == p_art and g not in a_data["genres"]:
                            a_data["genres"].append(g)

        artists_df = pd.DataFrame(list(unique_artists.values()))
        if "popularity" in cleaned_df.columns and len(artists_df) > 0:
            # Approximate artist popularity from tracks
            art_pop = cleaned_df.groupby("primary_artist")["popularity"].mean().to_dict()
            artists_df["popularity"] = artists_df["name"].map(art_pop).fillna(50).astype(int)
        else:
            artists_df["popularity"] = 50
        artists_df["image_url"] = None

        # 2. Albums Table
        album_map = {}
        album_records = []
        for _, row in cleaned_df.iterrows():
            a_title = str(row.get("album_name", f"{row['track_title']} (Single)")).strip()
            p_art_name = row["primary_artist"]
            album_key = f"{a_title.lower()}:::{p_art_name.lower()}"
            if album_key not in album_map:
                album_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, album_key))
                album_map[album_key] = album_id
                
                # Find matching artist_id
                p_art_id = next((a["id"] for a in unique_artists.values() if a["name"] == p_art_name), None)

                album_records.append({
                    "id": album_id,
                    "spotify_album_id": album_id,
                    "title": a_title,
                    "artist_id": p_art_id,
                    "release_date": row.get("release_date"),
                    "release_date_precision": row.get("release_date_precision", "year"),
                    "total_tracks": 1,
                    "cover_image_url": None
                })

        albums_df = pd.DataFrame(album_records)

        # 3. Tracks Table
        track_records = []
        for _, row in cleaned_df.iterrows():
            a_title = str(row.get("album_name", f"{row['track_title']} (Single)")).strip()
            p_art_name = row["primary_artist"]
            album_key = f"{a_title.lower()}:::{p_art_name.lower()}"
            alb_id = album_map.get(album_key)

            track_records.append({
                "id": row["track_id"],
                "spotify_track_id": row["track_id"],
                "isrc": None,
                "title": row["track_title"],
                "album_id": alb_id,
                "duration_ms": int(row.get("duration_ms", 210000)) if pd.notna(row.get("duration_ms")) else 210000,
                "explicit": bool(row.get("explicit", False)),
                "preview_url": None
            })

        tracks_df = pd.DataFrame(track_records)

        # 4. Track Artists Table
        track_artists_df = pd.DataFrame(track_artists_records)[["track_id", "artist_id", "role", "is_primary"]]

        # 5. Audio Features Table
        audio_cols = [
            "danceability", "energy", "key", "loudness", "mode", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"
        ]
        audio_records = []
        for _, row in cleaned_df.iterrows():
            feat_rec = {"track_id": row["track_id"]}
            for col in audio_cols:
                val = row.get(col)
                if pd.notna(val):
                    feat_rec[col] = float(val) if col not in ["key", "mode", "time_signature"] else int(val)
                else:
                    feat_rec[col] = None
            audio_records.append(feat_rec)

        audio_features_df = pd.DataFrame(audio_records)

        # 6. Track Metrics Table
        metrics_records = []
        for _, row in cleaned_df.iterrows():
            pop_val = row.get("popularity")
            str_val = row.get("streams")
            metrics_records.append({
                "track_id": row["track_id"],
                "popularity": int(pop_val) if pd.notna(pop_val) else None,
                "streams": int(str_val) if pd.notna(str_val) else None
            })

        track_metrics_df = pd.DataFrame(metrics_records)

        return {
            "artists": artists_df,
            "albums": albums_df,
            "tracks": tracks_df,
            "track_artists": track_artists_df,
            "audio_features": audio_features_df,
            "track_metrics": track_metrics_df
        }

    def export_local_datasets(self, entities: Dict[str, pd.DataFrame], output_dir: Optional[Path] = None) -> List[Path]:
        """
        Exports all normalized entity DataFrames locally to Parquet and CSV files.
        Guarantees local functionality without requiring live database access.
        """
        target_dir = output_dir or PROCESSED_DATA_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        saved_paths: List[Path] = []

        for name, df in entities.items():
            csv_path = target_dir / f"{name}.csv"
            parquet_path = target_dir / f"{name}.parquet"

            df.to_csv(csv_path, index=False)
            try:
                df.to_parquet(parquet_path, index=False)
                saved_paths.append(parquet_path)
            except Exception as e:
                print(f"[SupabaseLoader] Parquet export note for {name}: {e}")

            saved_paths.append(csv_path)

        return saved_paths

    def load_to_supabase(
        self, 
        entities: Dict[str, pd.DataFrame], 
        allow_synthetic: bool = False
    ) -> Dict[str, Any]:
        """
        Executes idempotent batch upserts into Supabase respecting referential integrity:
        1. artists
        2. albums
        3. tracks
        4. track_artists
        5. audio_features
        6. track_metrics
        """
        if not self.is_connected():
            return {
                "success": False,
                "error": "Supabase client is not connected. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
                "loaded_counts": {}
            }

        # Guard: prevent loading synthetic data into live database unless explicitly flagged
        is_synthetic = any(
            "synth" in str(tid) for tid in entities["tracks"]["id"].head(5)
        )
        if is_synthetic and not allow_synthetic:
            return {
                "success": False,
                "error": "Refusing to load synthetic benchmark data into live Supabase without --benchmark flag.",
                "loaded_counts": {}
            }

        results = {}
        batch_size = self.config.batch_size

        try:
            # 1. Artists (conflict on id or spotify_artist_id)
            art_records = entities["artists"].to_dict(orient="records")
            self._batch_upsert("artists", art_records, on_conflict="spotify_artist_id", batch_size=batch_size)
            results["artists"] = len(art_records)

            # 2. Albums (conflict on id or spotify_album_id)
            alb_records = entities["albums"].to_dict(orient="records")
            self._batch_upsert("albums", alb_records, on_conflict="spotify_album_id", batch_size=batch_size)
            results["albums"] = len(alb_records)

            # 3. Tracks (conflict on id or spotify_track_id)
            trk_records = entities["tracks"].to_dict(orient="records")
            self._batch_upsert("tracks", trk_records, on_conflict="spotify_track_id", batch_size=batch_size)
            results["tracks"] = len(trk_records)

            # 4. Track Artists (conflict on track_id, artist_id)
            ta_records = entities["track_artists"].to_dict(orient="records")
            self._batch_upsert("track_artists", ta_records, on_conflict="track_id,artist_id", batch_size=batch_size)
            results["track_artists"] = len(ta_records)

            # 5. Audio Features (conflict on track_id)
            af_records = entities["audio_features"].to_dict(orient="records")
            self._batch_upsert("audio_features", af_records, on_conflict="track_id", batch_size=batch_size)
            results["audio_features"] = len(af_records)

            # 6. Track Metrics (conflict on track_id)
            tm_records = entities["track_metrics"].to_dict(orient="records")
            self._batch_upsert("track_metrics", tm_records, on_conflict="track_id", batch_size=batch_size)
            results["track_metrics"] = len(tm_records)

            return {
                "success": True,
                "error": None,
                "loaded_counts": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "loaded_counts": results
            }

    def _batch_upsert(self, table_name: str, records: List[Dict[str, Any]], on_conflict: str, batch_size: int = 500) -> None:
        """Helper to upsert records in chunks."""
        for i in range(0, len(records), batch_size):
            chunk = records[i:i + batch_size]
            # Replace NaNs with None for clean JSON serialization
            cleaned_chunk = [
                {k: (None if pd.isna(v) else v) for k, v in row.items()}
                for row in chunk
            ]
            self.client.table(table_name).upsert(cleaned_chunk, on_conflict=on_conflict).execute()
