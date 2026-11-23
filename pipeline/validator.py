"""
Validation and Quality Report Module for the Spotify Trends Data Engineering Pipeline.
Detects outliers, invalid ranges, missing values, and produces JSON and Markdown reports.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from pipeline.config import ValidationBounds, QUALITY_REPORTS_DIR


class SpotifyDataValidator:
    def __init__(self, bounds: Optional[ValidationBounds] = None):
        self.bounds = bounds or ValidationBounds()

    def detect_outliers_iqr(self, series: pd.Series, multiplier: float = 1.5) -> Dict[str, Any]:
        """Detects numerical outliers using the Interquartile Range (IQR) method."""
        clean_series = series.dropna()
        if len(clean_series) < 4:
            return {"count": 0, "lower_bound": None, "upper_bound": None}
        q25 = float(clean_series.quantile(0.25))
        q75 = float(clean_series.quantile(0.75))
        iqr = q75 - q25
        lower_bound = q25 - (multiplier * iqr)
        upper_bound = q75 + (multiplier * iqr)
        outliers = clean_series[(clean_series < lower_bound) | (clean_series > upper_bound)]
        return {
            "count": int(len(outliers)),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "min_outlier": float(outliers.min()) if len(outliers) > 0 else None,
            "max_outlier": float(outliers.max()) if len(outliers) > 0 else None
        }

    def validate_dataset(
        self, 
        cleaned_df: pd.DataFrame, 
        raw_df: pd.DataFrame, 
        track_artists: List[Dict[str, Any]], 
        cleaning_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes comprehensive validation on the cleaned dataset.
        Returns structured validation metrics dictionary.
        """
        total_records = len(cleaned_df)
        report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_input_records": len(raw_df),
                "cleaned_records": total_records,
                "duplicates_removed": cleaning_metadata.get("duplicates_removed", 0),
                "total_track_artist_associations": len(track_artists)
            },
            "missing_values": {},
            "range_validation": {},
            "audio_feature_validation": {},
            "outliers": {},
            "cleaning_decisions": cleaning_metadata.get("decisions", [])
        }

        # 1. Missing Values Analysis
        for col in cleaned_df.columns:
            missing_count = int(cleaned_df[col].isna().sum())
            missing_pct = round((missing_count / total_records) * 100, 2) if total_records > 0 else 0
            report["missing_values"][col] = {
                "missing_count": missing_count,
                "missing_percentage": missing_pct
            }

        # 2. Popularity Validation
        if "popularity" in cleaned_df.columns:
            pop_series = cleaned_df["popularity"].dropna()
            invalid_pop = pop_series[(pop_series < self.bounds.popularity_min) | (pop_series > self.bounds.popularity_max)]
            report["range_validation"]["popularity"] = {
                "present": True,
                "evaluated_count": len(pop_series),
                "invalid_count": int(len(invalid_pop)),
                "min": float(pop_series.min()) if len(pop_series) > 0 else None,
                "max": float(pop_series.max()) if len(pop_series) > 0 else None,
                "mean": round(float(pop_series.mean()), 2) if len(pop_series) > 0 else None
            }
        else:
            report["range_validation"]["popularity"] = {"present": False, "invalid_count": 0}

        # 3. Streams Validation
        if "streams" in cleaned_df.columns:
            streams_series = cleaned_df["streams"].dropna()
            invalid_streams = streams_series[streams_series < self.bounds.streams_min]
            report["range_validation"]["streams"] = {
                "present": True,
                "evaluated_count": len(streams_series),
                "invalid_count": int(len(invalid_streams)),
                "min": float(streams_series.min()) if len(streams_series) > 0 else None,
                "max": float(streams_series.max()) if len(streams_series) > 0 else None,
                "total_streams": float(streams_series.sum()) if len(streams_series) > 0 else 0
            }
        else:
            report["range_validation"]["streams"] = {"present": False, "invalid_count": 0}

        # 4. Release Date Validation
        invalid_dates = cleaned_df["release_date"].isna().sum() if "release_date" in cleaned_df.columns else total_records
        report["range_validation"]["release_date"] = {
            "total_with_date": int(total_records - invalid_dates),
            "missing_or_invalid_date_count": int(invalid_dates),
            "date_precisions": cleaned_df["release_date_precision"].value_counts().to_dict() if "release_date_precision" in cleaned_df.columns else {}
        }

        # 5. Audio Feature Bounds Validation
        audio_cols = {
            "danceability": (self.bounds.danceability_min, self.bounds.danceability_max),
            "energy": (self.bounds.energy_min, self.bounds.energy_max),
            "speechiness": (self.bounds.speechiness_min, self.bounds.speechiness_max),
            "acousticness": (self.bounds.acousticness_min, self.bounds.acousticness_max),
            "instrumentalness": (self.bounds.instrumentalness_min, self.bounds.instrumentalness_max),
            "liveness": (self.bounds.liveness_min, self.bounds.liveness_max),
            "valence": (self.bounds.valence_min, self.bounds.valence_max),
            "tempo": (self.bounds.tempo_min, self.bounds.tempo_max)
        }

        for feat, (b_min, b_max) in audio_cols.items():
            if feat in cleaned_df.columns:
                f_series = cleaned_df[feat].dropna()
                invalid_feat = f_series[(f_series < b_min) | (f_series > b_max)]
                report["audio_feature_validation"][feat] = {
                    "evaluated_count": len(f_series),
                    "invalid_count": int(len(invalid_feat)),
                    "min": round(float(f_series.min()), 3) if len(f_series) > 0 else None,
                    "max": round(float(f_series.max()), 3) if len(f_series) > 0 else None,
                    "mean": round(float(f_series.mean()), 3) if len(f_series) > 0 else None
                }

        # 6. Outlier Analysis
        for metric_col in ["streams", "popularity", "duration_ms", "tempo"]:
            if metric_col in cleaned_df.columns:
                report["outliers"][metric_col] = self.detect_outliers_iqr(cleaned_df[metric_col])

        return report

    def generate_reports(self, validation_report: Dict[str, Any], output_prefix: str = "quality_report") -> Tuple[Path, Path]:
        """
        Saves validation report to both JSON and Markdown formats in data/quality_reports/.
        Returns (json_path, markdown_path).
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{output_prefix}_{timestamp_str}.json"
        md_filename = f"{output_prefix}_{timestamp_str}.md"

        json_path = QUALITY_REPORTS_DIR / json_filename
        md_path = QUALITY_REPORTS_DIR / md_filename

        # Write JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2)

        # Write Markdown
        md_content = self._render_markdown_report(validation_report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return json_path, md_path

    @staticmethod
    def _render_markdown_report(report: Dict[str, Any]) -> str:
        s = report["summary"]
        rv = report["range_validation"]
        lines = [
            f"# Spotify Trends Data Quality Report",
            f"**Generated:** {report['timestamp']}",
            "",
            "## 1. Executive Summary",
            f"- **Total Input Records:** {s['total_input_records']}",
            f"- **Cleaned & Retained Records:** {s['cleaned_records']}",
            f"- **Duplicates Removed:** {s['duplicates_removed']}",
            f"- **Track-Artist Collaboration Associations:** {s['total_track_artist_associations']}",
            "",
            "## 2. Core Metrics Validation",
            "| Metric | Evaluated | Invalid Count | Range / Bounds | Status |",
            "|---|---|---|---|---|"
        ]

        # Popularity row
        if "popularity" in rv and rv["popularity"].get("present"):
            p = rv["popularity"]
            status = "✅ PASS" if p["invalid_count"] == 0 else f"⚠️ {p['invalid_count']} Out of Range"
            lines.append(f"| Popularity | {p['evaluated_count']} | {p['invalid_count']} | [{p['min']} - {p['max']}] (Mean: {p['mean']}) | {status} |")

        # Streams row
        if "streams" in rv and rv["streams"].get("present"):
            st = rv["streams"]
            status = "✅ PASS" if st["invalid_count"] == 0 else f"⚠️ {st['invalid_count']} Invalid"
            lines.append(f"| Streams | {st['evaluated_count']} | {st['invalid_count']} | Total: {int(st['total_streams']):,} | {status} |")

        # Release date row
        rd = rv.get("release_date", {})
        lines.append(f"| Release Date | {rd.get('total_with_date', 0)} | {rd.get('missing_or_invalid_date_count', 0)} | Precisions: {rd.get('date_precisions', {})} | {'✅ PASS' if rd.get('missing_or_invalid_date_count', 0) == 0 else 'ℹ️ Incomplete Dates Handled'} |")

        lines.extend([
            "",
            "## 3. Audio Features Range Verification",
            "| Feature | Evaluated | Invalid Count | Min | Max | Mean | Verification |",
            "|---|---|---|---|---|---|---|"
        ])

        for feat, data in report.get("audio_feature_validation", {}).items():
            status = "✅ VALID" if data["invalid_count"] == 0 else f"❌ {data['invalid_count']} Invalid"
            lines.append(f"| {feat} | {data['evaluated_count']} | {data['invalid_count']} | {data['min']} | {data['max']} | {data['mean']} | {status} |")

        lines.extend([
            "",
            "## 4. Statistical Outliers (IQR Method)",
            "| Field | Outlier Count | Lower Bound | Upper Bound | Range Encountered |",
            "|---|---|---|---|---|"
        ])

        for metric, data in report.get("outliers", {}).items():
            r_str = f"[{data.get('min_outlier')} - {data.get('max_outlier')}]" if data["count"] > 0 else "None"
            lines.append(f"| {metric} | {data['count']} | {data['lower_bound']} | {data['upper_bound']} | {r_str} |")

        lines.extend([
            "",
            "## 5. Pipeline Cleaning Decisions",
        ])
        for dec in report.get("cleaning_decisions", []):
            lines.append(f"- {dec}")

        return "\n".join(lines)
