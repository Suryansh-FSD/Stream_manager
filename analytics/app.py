"""
Spotify Trends Analytics Studio - Main Application Entrypoint.
A premium, dark music intelligence platform built with Streamlit, Plotly, and Pandas.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path when running via `streamlit run analytics/app.py`
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Spotify Trends • Analytics Studio",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Injection for Premium Spotify Aesthetic
CUSTOM_CSS = """
<style>
    /* Dark canvas backgrounds */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Minimalist header - unobtrusive */
    header[data-testid="stHeader"] {
        background-color: rgba(18, 18, 18, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        height: 2.2rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Main container: compact paddings so all content fits on screen */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    
    /* Responsive column spacing & prevent column squishing */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.85rem !important;
        align-items: stretch !important;
    }
    div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }
    
    /* Sidebar customization & compact footprint */
    section[data-testid="stSidebar"] {
        width: 275px !important;
        min-width: 240px !important;
        background-color: #181818 !important;
        border-right: 1px solid #282828 !important;
    }
    section[data-testid="stSidebar"] > div {
        padding: 1rem 0.85rem !important;
    }
    
    /* Headers and typography */
    h1 {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        margin-top: 0 !important;
        margin-bottom: 0.35rem !important;
        color: #FFFFFF !important;
    }
    h2 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.35rem !important;
        color: #FFFFFF !important;
    }
    h3 {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.35rem !important;
        color: #FFFFFF !important;
    }
    h4 {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.25rem !important;
        color: #E0E0E0 !important;
    }
    
    /* Streamlit Plotly Chart full width fit */
    div[data-testid="stPlotlyChart"] {
        width: 100% !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    div[data-testid="stPlotlyChart"] > div {
        width: 100% !important;
    }
    
    /* Streamlit Dataframe custom styling & responsiveness */
    div[data-testid="stDataFrame"] {
        background-color: #181818 !important;
        border: 1px solid #282828 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        width: 100% !important;
        overflow-x: auto !important;
    }
    
    /* Input widgets & selectboxes */
    div[data-baseweb="select"] > div {
        background-color: #242424 !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        min-height: 36px !important;
        font-size: 0.85rem !important;
    }
    
    /* Sliders */
    div[data-testid="stSlider"] > div > div > div > div {
        background-color: #1DB954 !important;
    }
    
    /* Radio buttons for navigation */
    div[role="radiogroup"] label {
        padding: 5px 10px !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        margin-bottom: 2px !important;
        transition: background 0.15s ease !important;
    }
    div[role="radiogroup"] label:hover {
        background: #282828 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1DB954 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: 500px !important;
        padding: 6px 20px !important;
        transition: transform 0.1s ease, background-color 0.1s ease !important;
    }
    .stButton > button:hover {
        background-color: #1ed760 !important;
        transform: scale(1.02) !important;
    }
    
    /* Custom smooth scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #121212;
    }
    ::-webkit-scrollbar-thumb {
        background: #282828;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3e3e3e;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Imports after Page Config
from analytics.utils.data_source import load_master_analytics_dataset
from analytics.utils.queries import apply_global_filters
from analytics.components.sidebar import render_sidebar
from analytics.pages import (
    overview,
    artist_intelligence,
    genre_intelligence,
    yearly_trends,
    audio_features,
    correlation_analysis,
    data_quality
)


def main():
    # 4. Load Master Analytics Dataset
    df_master, metadata = load_master_analytics_dataset()

    if df_master.empty:
        st.error("No processed data found. Please run the data engineering pipeline first:")
        st.code("python -m pipeline.run_pipeline --benchmark")
        return

    # 5. Render Sidebar & Collect Global Filters
    selected_page, applied_filters = render_sidebar(df_master, metadata)

    # 6. Apply Global Filters
    df_filtered = apply_global_filters(
        df_master,
        year_range=applied_filters.get("year_range"),
        selected_genres=applied_filters.get("selected_genres"),
        selected_artists=applied_filters.get("selected_artists"),
        popularity_range=applied_filters.get("popularity_range")
    )

    # 7. Page Routing
    if selected_page == "Music Industry Overview":
        overview.render(df_filtered, metadata)
    elif selected_page == "Artist Intelligence":
        artist_intelligence.render(df_filtered, metadata)
    elif selected_page == "Genre Intelligence":
        genre_intelligence.render(df_filtered, metadata)
    elif selected_page == "Yearly Music Trends":
        yearly_trends.render(df_filtered, metadata)
    elif selected_page == "Audio Feature Analysis":
        audio_features.render(df_filtered, metadata)
    elif selected_page == "Popularity & Correlation":
        correlation_analysis.render(df_filtered, metadata)
    elif selected_page == "Data Quality & Report":
        data_quality.render(df_filtered, metadata)
    else:
        overview.render(df_filtered, metadata)


if __name__ == "__main__":
    main()
