"""
Page 7: Data Quality and Report for Spotify Trends Analytics Studio.
"""
import streamlit as st
import pandas as pd

from analytics.components.header import render_header
from analytics.components.metric_cards import render_kpi_row
from analytics.utils.data_source import load_latest_quality_report


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Data Quality & Audit Report",
        subtitle="Verification findings, outlier detection, range audits, and cleaning decisions.",
        metadata=metadata
    )

    report = load_latest_quality_report()

    if not report:
        st.warning("No data quality report found in `data/quality_reports/`. Run the pipeline to generate one:")
        st.code("python -m pipeline.run_pipeline --benchmark")
        return

    summary = report.get("summary", {})
    timestamp = report.get("timestamp", "N/A")
    filepath = report.get("_filepath", "Unknown")

    st.markdown(f"**Latest Audit Run:** `{timestamp}` • **Source File:** `{filepath}`")

    # 1. Summary KPIs
    render_kpi_row([
        {"title": "Input Records", "value": f"{summary.get('total_input_records', 0):,}", "subtitle": "Ingested rows"},
        {"title": "Retained Clean", "value": f"{summary.get('cleaned_records', 0):,}", "subtitle": "Valid catalogue rows"},
        {"title": "Duplicates Removed", "value": f"{summary.get('duplicates_removed', 0):,}", "subtitle": "Deduplicated"},
        {"title": "Artist Pairings", "value": f"{summary.get('total_track_artist_associations', 0):,}", "subtitle": "Normalized track-artist rows"}
    ])

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Core Metrics Range Validation
    st.markdown("### Core Metrics Range Verification")
    rv = report.get("range_validation", {})

    validation_rows = []
    if "popularity" in rv and rv["popularity"].get("present"):
        p = rv["popularity"]
        validation_rows.append({
            "Metric": "Popularity",
            "Evaluated Records": p.get("evaluated_count"),
            "Invalid Count": p.get("invalid_count"),
            "Observed Range": f"[{p.get('min')} - {p.get('max')}]",
            "Mean / Summary": f"Mean: {p.get('mean')}",
            "Status": "✅ PASS" if p.get("invalid_count") == 0 else "❌ FAILED"
        })

    if "streams" in rv and rv["streams"].get("present"):
        st_data = rv["streams"]
        validation_rows.append({
            "Metric": "Streams",
            "Evaluated Records": st_data.get("evaluated_count"),
            "Invalid Count": st_data.get("invalid_count"),
            "Observed Range": f"[{st_data.get('min')} - {st_data.get('max')}]",
            "Mean / Summary": f"Total: {int(st_data.get('total_streams', 0)):,}",
            "Status": "✅ PASS" if st_data.get("invalid_count") == 0 else "❌ FAILED"
        })

    if "release_date" in rv:
        rd = rv["release_date"]
        prec = rd.get("date_precisions", {})
        validation_rows.append({
            "Metric": "Release Date",
            "Evaluated Records": rd.get("total_with_date"),
            "Invalid Count": rd.get("missing_or_invalid_date_count"),
            "Observed Range": f"Precisions: {prec}",
            "Mean / Summary": f"{rd.get('total_with_date')} valid dates parsed",
            "Status": "✅ PASS" if rd.get("missing_or_invalid_date_count") == 0 else "ℹ️ Granular Dates"
        })

    if validation_rows:
        st.dataframe(pd.DataFrame(validation_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Audio Features Range Table
    st.markdown("### Audio Features Range & Bounds Verification")
    afv = report.get("audio_feature_validation", {})
    af_rows = []
    for feat, data in afv.items():
        af_rows.append({
            "Feature": feat.capitalize(),
            "Evaluated": data.get("evaluated_count"),
            "Invalid (Out of Bounds)": data.get("invalid_count"),
            "Min": data.get("min"),
            "Max": data.get("max"),
            "Mean": data.get("mean"),
            "Verification": "✅ VALID" if data.get("invalid_count") == 0 else "❌ INVALID"
        })

    if af_rows:
        st.dataframe(pd.DataFrame(af_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 4. Statistical Outliers Table (IQR)
    st.markdown("### Statistical Outlier Audit (1.5 × IQR Method)")
    outliers = report.get("outliers", {})
    out_rows = []
    for col, data in outliers.items():
        out_rows.append({
            "Metric / Field": col.capitalize(),
            "Outlier Count": data.get("count", 0),
            "Lower Bound": data.get("lower_bound"),
            "Upper Bound": data.get("upper_bound"),
            "Min Outlier": data.get("min_outlier"),
            "Max Outlier": data.get("max_outlier")
        })

    if out_rows:
        st.dataframe(pd.DataFrame(out_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 5. Cleaning Decisions Log
    st.markdown("### Pipeline Cleaning Decisions Log")
    decisions = report.get("cleaning_decisions", [])
    if decisions:
        st.markdown("""
        <div style="background: #181818; border: 1px solid #282828; border-radius: 8px; padding: 18px 24px; color: #CCCCCC; font-size: 0.88rem; line-height: 1.6;">
        """ + "".join([f"<div style='margin-bottom: 6px;'>• {d}</div>" for d in decisions]) + """
        </div>
        """, unsafe_allow_html=True)
