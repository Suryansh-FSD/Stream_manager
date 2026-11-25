"""
Sidebar Navigation and Global Filter Controls for Spotify Trends Analytics Studio.
"""
from typing import Dict, Any, Tuple, List
import streamlit as st
import pandas as pd

PAGE_OPTIONS = [
    "Music Industry Overview",
    "Artist Intelligence",
    "Genre Intelligence",
    "Yearly Music Trends",
    "Audio Feature Analysis",
    "Popularity & Correlation",
    "Data Quality & Report"
]


def render_sidebar(df: pd.DataFrame, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Renders custom sidebar navigation, global filter widgets, and footer branding.
    Returns (selected_page_name, applied_filters_dict).
    """
    with st.sidebar:
        # Branding Header
        st.markdown("""
        <div style="padding: 6px 0 14px 0; border-bottom: 1px solid #282828; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="background: #1DB954; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: bold; color: black; flex-shrink: 0;">
                    ♫
                </div>
                <div>
                    <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1;">Spotify Trends</div>
                    <div style="color: #1DB954; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">Analytics Studio</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Menu
        st.markdown("""<div style="color: #888888; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">NAVIGATE</div>""", unsafe_allow_html=True)
        selected_page = st.radio(
            "Navigation",
            PAGE_OPTIONS,
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("<hr style='border: 0; border-top: 1px solid #282828; margin: 16px 0 12px 0;'>", unsafe_allow_html=True)

        # Global Filters Header
        st.markdown("""<div style="color: #888888; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">GLOBAL FILTERS</div>""", unsafe_allow_html=True)

        applied_filters: Dict[str, Any] = {}

        if not df.empty:
            # 1. Year Range Filter
            if "release_year" in df.columns:
                valid_years = df["release_year"].dropna().astype(int)
                if not valid_years.empty:
                    min_yr, max_yr = int(valid_years.min()), int(valid_years.max())
                    if min_yr < max_yr:
                        year_range = st.slider(
                            "Release Year Range",
                            min_value=min_yr,
                            max_value=max_yr,
                            value=(min_yr, max_yr),
                            step=1
                        )
                        applied_filters["year_range"] = year_range
                    else:
                        applied_filters["year_range"] = (min_yr, max_yr)

            # 2. Genre Filter
            if "primary_genre" in df.columns:
                available_genres = sorted([g for g in df["primary_genre"].unique() if g and g != "Uncategorized"])
                genre_options = ["All Genres"] + available_genres
                selected_genres = st.multiselect(
                    "Genres",
                    options=genre_options,
                    default=["All Genres"]
                )
                applied_filters["selected_genres"] = selected_genres

            # 3. Artist Filter
            if "primary_artist_name" in df.columns:
                available_artists = sorted([a for a in df["primary_artist_name"].unique() if a and a != "Unknown Artist"])
                artist_options = ["All Artists"] + available_artists
                selected_artists = st.multiselect(
                    "Artists",
                    options=artist_options,
                    default=["All Artists"]
                )
                applied_filters["selected_artists"] = selected_artists

            # 4. Popularity Range Filter
            if "popularity" in df.columns:
                pop_series = df["popularity"].dropna()
                min_p = int(pop_series.min()) if not pop_series.empty else 0
                max_p = int(pop_series.max()) if not pop_series.empty else 100
                if min_p < max_p:
                    pop_range = st.slider(
                        "Popularity Range",
                        min_value=0,
                        max_value=100,
                        value=(min_p, max_p),
                        step=5
                    )
                    applied_filters["popularity_range"] = pop_range

        st.markdown("<hr style='border: 0; border-top: 1px solid #282828; margin: 16px 0 12px 0;'>", unsafe_allow_html=True)

        # Footer Status Card
        mode_text = "Supabase PostgreSQL" if metadata.get("mode") == "supabase" else "Local Parquet"
        st.markdown(f"""
        <div style="background: #181818; border: 1px solid #282828; border-radius: 8px; padding: 10px; font-size: 0.72rem; color: #888888;">
            <div style="font-weight: 600; color: #FFFFFF; margin-bottom: 3px;">System Engine</div>
            <div>Source: <span style="color: #1DB954;">{mode_text}</span></div>
            <div>Engine: <span style="color: #E0E0E0;">Active (@st.cache_data)</span></div>
        </div>
        """, unsafe_allow_html=True)

        return selected_page, applied_filters
