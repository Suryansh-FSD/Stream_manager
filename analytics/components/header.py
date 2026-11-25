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
    col_title, col_status = st.columns([3.5, 1.2])

    with col_title:
        title_html = (
            f'<div style="margin-bottom:4px;">'
            f'<div style="color:#1DB954;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:2px;">Spotify Trends • Analytics Studio</div>'
            f'<h1 style="color:#FFFFFF;font-size:1.75rem;font-weight:800;margin:0;padding:0;letter-spacing:-0.5px;line-height:1.2;">{title}</h1>'
            f'<p style="color:#A0A0A0;font-size:0.88rem;margin-top:3px;margin-bottom:8px;line-height:1.4;">{subtitle}</p>'
            f'</div>'
        )
        st.markdown(title_html, unsafe_allow_html=True)

    with col_status:
        mode_label = "Cloud Supabase" if metadata.get("mode") == "supabase" else "Local Parquet"
        mode_color = "#1DB954" if metadata.get("mode") == "supabase" else "#38bdf8"
        record_cnt = metadata.get("record_count", 0)

        badge_html = (
            f'<div style="background:#181818;border:1px solid #282828;border-radius:8px;padding:8px 12px;text-align:right;margin-top:2px;">'
            f'<div style="font-size:0.68rem;color:#888888;text-transform:uppercase;letter-spacing:0.5px;">Engine Source</div>'
            f'<div style="font-size:0.85rem;font-weight:700;color:{mode_color};margin-top:1px;">● {mode_label}</div>'
            f'<div style="font-size:0.72rem;color:#B3B3B3;margin-top:1px;">{record_cnt:,} records active</div>'
            f'</div>'
        )
        st.markdown(badge_html, unsafe_allow_html=True)

    # Synthetic Benchmark Disclaimer Banner
    if metadata.get("is_synthetic", True):
        banner_html = (
            f'<div style="background:rgba(29, 185, 84, 0.08);border-left:3px solid #1DB954;padding:6px 12px;border-radius:4px;margin-bottom:14px;display:flex;align-items:center;gap:8px;">'
            f'<span style="color:#1DB954;font-weight:700;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.5px;">Synthetic Benchmark:</span>'
            f'<span style="color:#CCCCCC;font-size:0.78rem;">Verified local demonstration dataset for academic evaluation. Metrics reflect normalized benchmark values.</span>'
            f'</div>'
        )
        st.markdown(banner_html, unsafe_allow_html=True)

