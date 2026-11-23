"""
Spotify Trends Analytics Studio - Main Application Entrypoint.
A premium, dark music intelligence platform built with Streamlit, Plotly, and Pandas.
"""
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
    
    /* Sidebar customization */
    section[data-testid="stSidebar"] {
        background-color: #181818 !important;
        border-right: 1px solid #282828 !important;
    }
    
    /* Headers and typography */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 96% !important;
    }
    
    /* Input widgets & selectboxes */
    div[data-baseweb="select"] > div {
        background-color: #242424 !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
    }
    
    /* Streamlit Dataframe custom styling */
    div[data-testid="stDataFrame"] {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 4px;
    }
    
    /* Sliders */
    div[data-testid="stSlider"] > div > div > div > div {
        background-color: #1DB954 !important;
    }
    
    /* Radio buttons for navigation */
    div[role="radiogroup"] label {
        padding: 6px 12px !important;
        border-radius: 6px !important;
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
        border: none !important;
        border-radius: 500px !important;
        padding: 8px 24px !important;
        transition: transform 0.1s ease, background-color 0.1s ease !important;
    }
    .stButton > button:hover {
        background-color: #1ed760 !important;
        transform: scale(1.02) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
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
