"""
Command-line Execution Runner for the Spotify Trends Data Engineering Pipeline.
Supports real dataset cleaning, benchmark processing, report generation,
local export, and optional Supabase upserts.
"""
import argparse
import sys
from pathlib import Path
import pandas as pd

from pipeline.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, QUALITY_REPORTS_DIR, PipelineConfig
from pipeline.cleaner import SpotifyDataCleaner
from pipeline.validator import SpotifyDataValidator
from pipeline.loader import SupabaseLoader


def run_pipeline(
    input_path: str, 
    is_benchmark: bool = False, 
    load_supabase: bool = False
) -> int:
    """
    Main orchestration routine for the data pipeline.
    """
    csv_file = Path(input_path)
    if not csv_file.exists():
        print(f"\n[ERROR] Input dataset file not found: {csv_file.resolve()}", file=sys.stderr)
        print("Please verify the filepath or generate benchmark data with:", file=sys.stderr)
        print("  python -m pipeline.generate_benchmark_data\n", file=sys.stderr)
        return 1

    print(f"\n=======================================================")
    print(f"🎵 SPOTIFY TRENDS DATA ENGINEERING PIPELINE")
    print(f"=======================================================")
    print(f"Input Dataset : {csv_file.resolve()}")
    print(f"Mode          : {'SYNTHETIC BENCHMARK' if is_benchmark else 'REAL DATA'}")
    print(f"Supabase Load : {load_supabase}")
    print(f"=======================================================\n")

    # Step 1: Ingestion
    print(f"📥 [Step 1/5] Ingesting CSV dataset...")
    try:
        raw_df = pd.read_csv(csv_file, low_memory=False)
        print(f"   Successfully loaded {len(raw_df)} records across {len(raw_df.columns)} columns.")
    except Exception as e:
        print(f"\n[ERROR] Failed to read CSV: {e}", file=sys.stderr)
        return 1

    # Step 2: Cleaning & Normalization
    print(f"\n🧹 [Step 2/5] Cleaning, normalizing, and resolving collaborations...")
    cleaner = SpotifyDataCleaner()
    try:
        cleaned_df, raw_df, track_artists, cleaning_metadata = cleaner.clean_dataset(raw_df)
        print(f"   Cleaned records : {len(cleaned_df)}")
        print(f"   Duplicates removed : {cleaning_metadata['duplicates_removed']}")
        print(f"   Collaborations processed : {len(track_artists)} track-artist pairings")
    except ValueError as ve:
        print(f"\n[ERROR] Schema Validation Error: {ve}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during cleaning: {e}", file=sys.stderr)
        return 1

    # Step 3: Statistical Validation & Quality Reporting
    print(f"\n📊 [Step 3/5] Validating audio features, popularity, streams, and outliers...")
    validator = SpotifyDataValidator()
    validation_report = validator.validate_dataset(cleaned_df, raw_df, track_artists, cleaning_metadata)
    
    prefix = "benchmark_quality_report" if is_benchmark else "quality_report"
    json_path, md_path = validator.generate_reports(validation_report, output_prefix=prefix)
    print(f"   ✅ Data Quality Report (JSON)     : {json_path}")
    print(f"   ✅ Data Quality Report (Markdown) : {md_path}")

    # Step 4: Normalizing Relational Entities & Local Export
    print(f"\n💾 [Step 4/5] Deconstructing star schema & exporting local Parquet/CSV...")
    loader = SupabaseLoader()
    entities = loader.prepare_relational_tables(cleaned_df, track_artists)
    exported_files = loader.export_local_datasets(entities)

    for ent_name, ent_df in entities.items():
        print(f"   - {ent_name:15}: {len(ent_df):5d} records")
    print(f"   Successfully exported {len(exported_files)} files to: {PROCESSED_DATA_DIR}")

    # Step 5: Database Loading
    print(f"\n🚀 [Step 5/5] Supabase Database Integration...")
    if load_supabase:
        if not loader.is_connected():
            print("   ⚠️  Supabase credentials not configured in environment.")
            print("      To load data into live Supabase, configure in .env:")
            print("        NEXT_PUBLIC_SUPABASE_URL=...")
            print("        SUPABASE_SERVICE_ROLE_KEY=...")
            print("      Skipping remote database upsert (local data export is complete).")
        else:
            print("   Connecting to Supabase and executing batch upserts...")
            db_res = loader.load_to_supabase(entities, allow_synthetic=is_benchmark)
            if db_res["success"]:
                print("   ✅ Supabase upserts complete:")
                for tbl, cnt in db_res["loaded_counts"].items():
                    print(f"      - {tbl}: {cnt} rows upserted")
            else:
                print(f"   ❌ Supabase load skipped or failed: {db_res['error']}")
    else:
        print("   ℹ️  Database load flag not set (--load-supabase omitted).")
        print("      Data successfully processed and stored locally.")

    print(f"\n=======================================================")
    print(f"✨ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"=======================================================\n")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Spotify Trends Data Engineering Pipeline.")
    parser.add_argument(
        "--input", 
        type=str, 
        default=str(RAW_DATA_DIR / "benchmark_spotify.csv"),
        help="Path to input raw Spotify CSV."
    )
    parser.add_argument(
        "--benchmark", 
        action="store_true", 
        help="Flag indicating input is synthetic benchmark data."
    )
    parser.add_argument(
        "--load-supabase", 
        action="store_true", 
        help="Attempt to load processed entities into Supabase PostgreSQL."
    )
    args = parser.parse_args()

    sys.exit(run_pipeline(
        input_path=args.input, 
        is_benchmark=args.benchmark, 
        load_supabase=args.load_supabase
    ))


if __name__ == "__main__":
    main()
