"""
Cleaner module for the Spotify Trends Data Engineering Pipeline.
Handles column normalization, deduplication, multi-artist splitting,
date normalization, and type conversion.
"""
import re
import uuid
import hashlib
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

from pipeline.config import ColumnMapping, ValidationBounds


class SpotifyDataCleaner:
    def __init__(self, column_mapping: Optional[ColumnMapping] = None, bounds: Optional[ValidationBounds] = None):
        self.mapping = column_mapping or ColumnMapping()
        self.bounds = bounds or ValidationBounds()
        self.cleaning_decisions: List[str] = []

    def log_decision(self, message: str) -> None:
        self.cleaning_decisions.append(message)

    def standardize_column_names(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Maps raw input column names to canonical schema names using ColumnMapping aliases.
        """
        raw_cols = df.columns.tolist()
        canonical_map: Dict[str, str] = {}
        reversed_field_map = {}

        # Build alias lookup
        for canonical_name in self.mapping.__dataclass_fields__:
            aliases = getattr(self.mapping, canonical_name)
            for alias in aliases:
                norm_alias = alias.strip().lower().replace(" ", "_")
                reversed_field_map[norm_alias] = canonical_name

        for col in raw_cols:
            clean_col = str(col).strip().lower().replace(" ", "_")
            if clean_col in reversed_field_map:
                target = reversed_field_map[clean_col]
                # Avoid duplicate mapping if already assigned
                if target not in canonical_map.values():
                    canonical_map[col] = target

        renamed_df = df.rename(columns=canonical_map)
        self.log_decision(f"Mapped {len(canonical_map)} columns from input: {canonical_map}")
        return renamed_df, canonical_map

    @staticmethod
    def generate_deterministic_id(title: str, artist: str) -> str:
        """Generates a reproducible UUIDv5 for tracks or artists lacking Spotify IDs."""
        key = f"{str(title).strip().lower()}:::{str(artist).strip().lower()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))

    @staticmethod
    def normalize_artist_name(name: str) -> str:
        """Cleans whitespace, surrounding quotes, and formatting in artist names."""
        if not name or pd.isna(name):
            return "Unknown Artist"
        cleaned = str(name).strip().strip("'\"`")
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def split_artists(self, raw_artist_string: str) -> List[Dict[str, Any]]:
        """
        Splits collaboration strings into individual artists while respecting 
        known band names (e.g. AC/DC) and assigning primary/featured roles.
        """
        if not raw_artist_string or pd.isna(raw_artist_string):
            return [{"name": "Unknown Artist", "role": "main", "is_primary": True}]

        s = str(raw_artist_string).strip()

        # Temporary protect protected tokens like AC/DC
        protected = {"AC/DC": "__AC_DC__"}
        for k, v in protected.items():
            s = s.replace(k, v)

        # Split on feat., ft., with, &, ;, and commas
        pattern = r"(?:\s*feat\.?\s*|\s*ft\.?\s*|\s*with\s*|\s*&\s*|\s*;\s*|,\s*)"
        parts = re.split(pattern, s, flags=re.IGNORECASE)

        artists = []
        for idx, part in enumerate(parts):
            name = part.strip()
            for k, v in protected.items():
                name = name.replace(v, k)
            name = self.normalize_artist_name(name)
            if name and name != "Unknown Artist":
                artists.append({
                    "name": name,
                    "role": "main" if idx == 0 else "featured",
                    "is_primary": (idx == 0)
                })

        if not artists:
            return [{"name": "Unknown Artist", "role": "main", "is_primary": True}]

        return artists

    def parse_release_date(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        """
        Parses release dates into standard YYYY-MM-DD format and tracks precision.
        Handles either a single release_date string or split year/month/day columns.
        Returns (formatted_date_string, precision).
        """
        # Case 1: Separate year, month, day columns
        if "release_year" in row and pd.notna(row["release_year"]):
            try:
                y = int(float(row["release_year"]))
                m = int(float(row.get("release_month", 1))) if pd.notna(row.get("release_month")) else 1
                d = int(float(row.get("release_day", 1))) if pd.notna(row.get("release_day")) else 1
                
                # Clamp month and day
                m = max(1, min(12, m))
                d = max(1, min(31, d))

                precision = "day" if ("release_day" in row and pd.notna(row["release_day"])) else (
                    "month" if ("release_month" in row and pd.notna(row["release_month"])) else "year"
                )
                return f"{y:04d}-{m:02d}-{d:02d}", precision
            except Exception:
                pass

        # Case 2: String release_date column
        if "release_date" in row and pd.notna(row["release_date"]):
            val = str(row["release_date"]).strip()
            # Match YYYY-MM-DD
            m_day = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", val)
            if m_day:
                y, m, d = int(m_day.group(1)), int(m_day.group(2)), int(m_day.group(3))
                m = max(1, min(12, m))
                d = max(1, min(31, d))
                return f"{y:04d}-{m:02d}-{d:02d}", "day"
            
            # Match YYYY-MM
            m_month = re.match(r"^(\d{4})[-/](\d{1,2})", val)
            if m_month:
                y, m = int(m_month.group(1)), int(m_month.group(2))
                m = max(1, min(12, m))
                return f"{y:04d}-{m:02d}-01", "month"

            # Match YYYY
            m_year = re.match(r"^(\d{4})", val)
            if m_year:
                y = int(m_year.group(1))
                return f"{y:04d}-01-01", "year"

        return None, None

    def clean_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes full data cleaning workflow.
        Returns:
            - cleaned_df: Normalized master track dataset
            - raw_df: Original unmodified input
            - track_artists_records: Normalized artist-track associations
            - metadata: Processing summary statistics
        """
        raw_df = df.copy()
        working_df, col_map = self.standardize_column_names(df)

        initial_count = len(working_df)
        self.log_decision(f"Starting cleaning on {initial_count} raw records.")

        # Ensure essential columns exist
        if "track_title" not in working_df.columns:
            raise ValueError("Input dataset is missing required track title/name column.")
        if "artist_name" not in working_df.columns:
            raise ValueError("Input dataset is missing required artist name column.")

        # Strip whitespace on string columns
        for str_col in ["track_title", "artist_name", "album_name", "genre"]:
            if str_col in working_df.columns:
                working_df[str_col] = working_df[str_col].astype(str).str.strip()

        # Handle numeric conversion and percentage scaling (e.g. Kaggle 2023 has energy_%, danceability_%)
        percentage_cols = ["danceability", "energy", "speechiness", "acousticness", 
                           "instrumentalness", "liveness", "valence"]
        for p_col in percentage_cols:
            if p_col in working_df.columns:
                # Convert to numeric safely
                working_df[p_col] = pd.to_numeric(working_df[p_col], errors="coerce")
                # If values are in 0-100 scale, normalize to 0.0-1.0
                if (working_df[p_col].max(skipna=True) or 0) > 1.0:
                    working_df[p_col] = working_df[p_col] / 100.0
                    self.log_decision(f"Normalized '{p_col}' from percentage scale [0, 100] to [0.0, 1.0].")

        # Convert numeric fields
        for num_col in ["popularity", "duration_ms", "loudness", "tempo", "key", "mode", "time_signature"]:
            if num_col in working_df.columns:
                working_df[num_col] = pd.to_numeric(working_df[num_col], errors="coerce")

        # Explicit conversion for streams (remove commas if string like '1,234,567')
        if "streams" in working_df.columns:
            if working_df["streams"].dtype == object:
                working_df["streams"] = working_df["streams"].astype(str).str.replace(",", "").str.strip()
            working_df["streams"] = pd.to_numeric(working_df["streams"], errors="coerce")
            self.log_decision("Processed streams column as numerical bigint without inferring from popularity.")

        # Explicit column boolean conversion
        if "explicit" in working_df.columns:
            working_df["explicit"] = working_df["explicit"].apply(
                lambda x: True if str(x).lower() in ["true", "1", "yes", "t"] else False
            )
        else:
            working_df["explicit"] = False

        # Parse release dates
        parsed_dates = []
        date_precisions = []
        for _, row in working_df.iterrows():
            d_str, prec = self.parse_release_date(row)
            parsed_dates.append(d_str)
            date_precisions.append(prec)

        working_df["release_date"] = parsed_dates
        working_df["release_date_precision"] = date_precisions

        # Parse album name if missing
        if "album_name" not in working_df.columns or working_df["album_name"].isna().all():
            working_df["album_name"] = working_df["track_title"] + " (Single)"
            self.log_decision("Populated missing album names with '[Track Title] (Single)'.")

        # Deduplication logic
        # Canonical duplicate key: normalized title + primary artist
        working_df["_clean_title"] = working_df["track_title"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
        working_df["_clean_artist"] = working_df["artist_name"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

        # Prioritize records with non-null streams / higher popularity during deduplication
        sort_cols = []
        if "streams" in working_df.columns:
            sort_cols.append("streams")
        if "popularity" in working_df.columns:
            sort_cols.append("popularity")

        if sort_cols:
            working_df = working_df.sort_values(by=sort_cols, ascending=False)

        pre_dedupe_count = len(working_df)
        working_df = working_df.drop_duplicates(subset=["_clean_title", "_clean_artist"], keep="first")
        duplicates_removed = pre_dedupe_count - len(working_df)
        self.log_decision(f"Detected and removed {duplicates_removed} duplicate track records.")

        # Assign / validate track_id
        if "track_id" not in working_df.columns:
            working_df["track_id"] = [
                self.generate_deterministic_id(row["track_title"], row["artist_name"])
                for _, row in working_df.iterrows()
            ]
        else:
            # Replace null track_ids with deterministic IDs
            working_df["track_id"] = working_df.apply(
                lambda r: r["track_id"] if pd.notna(r["track_id"]) and str(r["track_id"]).strip() != ""
                else self.generate_deterministic_id(r["track_title"], r["artist_name"]),
                axis=1
            )

        # Multi-artist parsing and association table generation
        track_artists_records: List[Dict[str, Any]] = []
        primary_artists = []

        for _, row in working_df.iterrows():
            t_id = row["track_id"]
            artist_list = self.split_artists(row["artist_name"])
            primary_artists.append(artist_list[0]["name"])
            for art in artist_list:
                art_id = self.generate_deterministic_id("artist", art["name"])
                track_artists_records.append({
                    "track_id": t_id,
                    "artist_id": art_id,
                    "artist_name": art["name"],
                    "role": art["role"],
                    "is_primary": art["is_primary"]
                })

        working_df["primary_artist"] = primary_artists

        # Clean helper columns
        working_df = working_df.drop(columns=["_clean_title", "_clean_artist"], errors="ignore")

        metadata = {
            "initial_record_count": initial_count,
            "cleaned_record_count": len(working_df),
            "duplicates_removed": duplicates_removed,
            "track_artists_associations_count": len(track_artists_records),
            "decisions": self.cleaning_decisions
        }

        return working_df, raw_df, track_artists_records, metadata
