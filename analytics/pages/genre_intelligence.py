"""
Page 3: Genre Intelligence for Spotify Trends Analytics Studio.
"""
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import pandas as pd

from analytics.components.header import render_header
from analytics.components.metric_cards import render_kpi_row
from analytics.components.charts import (
    create_horizontal_bar_chart, create_pie_chart, 
    create_vertical_bar_chart, create_radar_chart
)
from analytics.utils.queries import get_genre_metrics_summary
from analytics.utils.formatting import format_number


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Genre Intelligence",
        subtitle="Cross-genre performance, streaming shares, and acoustic characteristics.",
        metadata=metadata
    )

    if df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    genre_summary = get_genre_metrics_summary(df)
    if genre_summary.empty:
        st.info("No genre metrics available for current selection.")
        return

    # 1. Top Genres KPI Row
    top_genre = genre_summary.iloc[0]
    total_genres = len(genre_summary)
    render_kpi_row([
        {"title": "Active Genres", "value": str(total_genres), "subtitle": "In filtered catalog"},
        {"title": "Top Genre", "value": top_genre["primary_genre"], "subtitle": f"{format_number(top_genre['streams'])} streams"},
        {"title": "Highest Popularity", "value": f"{genre_summary.sort_values(by='popularity', ascending=False).iloc[0]['primary_genre']}", "subtitle": f"{genre_summary['popularity'].max():.1f}/100 score"},
        {"title": "Most Energetic", "value": f"{genre_summary.sort_values(by='energy', ascending=False).iloc[0]['primary_genre']}", "subtitle": f"{genre_summary['energy'].max():.2f} avg energy"}
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. Charts Grid
    col_share, col_streams = st.columns(2)

    with col_share:
        st.markdown("### Genre Streaming Share")
        fig_pie = create_pie_chart(
            genre_summary,
            names_col="primary_genre",
            values_col="streams",
            title="Market Streaming Share by Genre"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_streams:
        st.markdown("### Total Streams by Genre")
        fig_bar = create_horizontal_bar_chart(
            genre_summary,
            x_col="streams",
            y_col="primary_genre",
            title="Total Cumulative Streams per Genre"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Audio Features across Genres
    st.markdown("### Musical Profiles across Genres")
    col_feat1, col_feat2 = st.columns(2)

    with col_feat1:
        if "danceability" in genre_summary.columns:
            fig_dance = create_vertical_bar_chart(
                genre_summary,
                x_col="primary_genre",
                y_col="danceability",
                title="Average Danceability by Genre",
                color_discrete_sequence=["#1DB954"]
            )
            st.plotly_chart(fig_dance, use_container_width=True)

    with col_feat2:
        if "energy" in genre_summary.columns:
            fig_energy = create_vertical_bar_chart(
                genre_summary,
                x_col="primary_genre",
                y_col="energy",
                title="Average Energy by Genre",
                color_discrete_sequence=["#38bdf8"]
            )
            st.plotly_chart(fig_energy, use_container_width=True)

    # 4. Genre Data Table
    st.markdown("### Genre Metrics Breakdown")
    table_genre = genre_summary.copy()
    table_genre["streams"] = table_genre["streams"].apply(format_number)
    st.dataframe(table_genre, use_container_width=True, hide_index=True)
