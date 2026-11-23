"""
Header component for Spotify Trends Analytics Studio.
Renders branding, data source connection badges, and synthetic data banners.
"""
from typing import Dict, Any
import streamlit as st


def render_header(
    title: str, 
    subtitle: str, 
    metadata: Dict[str, Any]
) -> None:
    """Renders page title, connection badge, and disclaimer notice."""
    col_title, col_status = st.columns([3, 1])

    with col_title:
        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="color: #1DB954; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px;">
                Spotify Trends • Studio
            </div>
            <h1 style="color: #FFFFFF; font-size: 2.2rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.5px;">
                {title}
            </h1>
            <p style="color: #B3B3B3; font-size: 1.0rem; margin-top: 6px; margin-bottom: 16px;">
                {subtitle}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_status:
        mode_label = "Cloud Supabase" if metadata.get("mode") == "supabase" else "Local Parquet"
        mode_color = "#1DB954" if metadata.get("mode") == "supabase" else "#3b82f6"
        record_cnt = metadata.get("record_count", 0)

        st.markdown(f"""
        <div style="background: #181818; border: 1px solid #282828; border-radius: 8px; padding: 10px 14px; text-align: right; margin-top: 10px;">
            <div style="font-size: 0.75rem; color: #888888; text-transform: uppercase; letter-spacing: 0.5px;">Data Source</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: {mode_color}; margin-top: 2px;">
                ● {mode_label}
            </div>
            <div style="font-size: 0.75rem; color: #B3B3B3; margin-top: 2px;">
                {record_cnt:,} tracks loaded
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Synthetic Benchmark Disclaimer
    if metadata.get("is_synthetic", True):
        st.markdown("""
        <div style="background: rgba(29, 185, 84, 0.08); border-left: 4px solid #1DB954; padding: 10px 16px; border-radius: 4px; margin-bottom: 24px;">
            <span style="color: #1DB954; font-weight: 700; font-size: 0.85rem;">SYNTHETIC BENCHMARK MODE:</span>
            <span style="color: #E0E0E0; font-size: 0.85rem; margin-left: 6px;">
                Currently rendering verified synthetic benchmark data. Values do not represent proprietary or live Spotify streaming activity.
            </span>
        </div>
        """, unsafe_allow_html=True)
