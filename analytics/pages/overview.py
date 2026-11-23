"""
Page 1: Music Industry Overview for Spotify Trends Analytics Studio.
"""
import streamlit as st
import pandas as pd

from analytics.components.header import render_header
from analytics.components.metric_cards import render_kpi_row
from analytics.components.charts import (
    create_horizontal_bar_chart, create_vertical_bar_chart, 
    create_pie_chart, create_line_chart, create_radar_chart
)
from analytics.utils.queries import (
    get_executive_kpis, get_top_tracks_by_streams, 
    get_top_artists_by_streams, get_genre_metrics_summary, get_yearly_cohort_summary
)
from analytics.utils.formatting import format_number, format_duration


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Music Industry Overview",
        subtitle="Executive streaming benchmarks, catalogue volume, and high-level audio indicators.",
        metadata=metadata
    )

    if df.empty:
        st.warning("No records match the selected filter criteria. Please adjust your global filters.")
        return

    # 1. Executive KPI Cards
    kpis = get_executive_kpis(df)
    render_kpi_row([
        {"title": "Total Tracks", "value": f"{kpis['total_tracks']:,}", "subtitle": "Cataloged tracks"},
        {"title": "Total Streams", "value": format_number(kpis["total_streams"]), "subtitle": "Cumulative streams"},
        {"title": "Unique Artists", "value": f"{kpis['unique_artists']:,}", "subtitle": "Primary creators"},
        {"title": "Active Genres", "value": f"{kpis['unique_genres']:,}", "subtitle": "Musical genres"},
        {"title": "Avg Popularity", "value": f"{kpis['avg_popularity']}/100", "subtitle": "Market score"},
        {"title": "Avg Track Length", "value": format_duration(kpis["avg_duration_sec"] * 1000), "subtitle": "Mean duration"}
    ])

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Top Tracks & Top Artists Grid
    col_tracks, col_artists = st.columns(2)

    with col_tracks:
        st.markdown("### Top Tracks by Streams")
        top_tracks = get_top_tracks_by_streams(df, limit=10)
        if not top_tracks.empty:
            top_tracks["display_name"] = top_tracks["title"] + " - " + top_tracks["primary_artist_name"]
            fig_tracks = create_horizontal_bar_chart(
                top_tracks,
                x_col="streams",
                y_col="display_name",
                title="Top 10 Tracks (Actual Streams)"
            )
            st.plotly_chart(fig_tracks, use_container_width=True)
        else:
            st.info("No stream data available for current selection.")

    with col_artists:
        st.markdown("### Top Artists by Streams")
        top_artists = get_top_artists_by_streams(df, limit=10)
        if not top_artists.empty:
            fig_artists = create_horizontal_bar_chart(
                top_artists,
                x_col="total_streams",
                y_col="primary_artist_name",
                title="Top 10 Primary Artists (Uniquely Attributable Streams)"
            )
            st.plotly_chart(fig_artists, use_container_width=True)
        else:
            st.info("No artist data available for current selection.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Genre Distribution & Release Cohorts
    col_genre, col_year = st.columns(2)

    with col_genre:
        st.markdown("### Genre Distribution")
        genre_summary = get_genre_metrics_summary(df)
        if not genre_summary.empty:
            fig_genre = create_pie_chart(
                genre_summary.head(8),
                names_col="primary_genre",
                values_col="streams",
                title="Streaming Share by Top Genres"
            )
            st.plotly_chart(fig_genre, use_container_width=True)
        else:
            st.info("No genre data available.")

    with col_year:
        st.markdown("### Release-Year Distribution")
        yearly_summary = get_yearly_cohort_summary(df)
        if not yearly_summary.empty:
            fig_year = create_line_chart(
                yearly_summary,
                x_col="release_year",
                y_col="track_count",
                title="Catalog Tracks by Release Year"
            )
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("No release date data available.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 4. Derived Data Observations
    st.markdown("### Executive Observations")
    top_genre_name = genre_summary.iloc[0]["primary_genre"] if not genre_summary.empty else "N/A"
    top_artist_name = top_artists.iloc[0]["primary_artist_name"] if not top_artists.empty else "N/A"
    top_artist_streams = format_number(top_artists.iloc[0]["total_streams"]) if not top_artists.empty else "N/A"

    st.markdown(f"""
    <div style="background: #181818; border: 1px solid #282828; border-radius: 8px; padding: 18px 24px; color: #E0E0E0; font-size: 0.92rem; line-height: 1.6;">
        <ul style="margin: 0; padding-left: 20px;">
            <li><strong>Leading Creator:</strong> <code>{top_artist_name}</code> accounts for the highest single-artist stream attribution with <strong>{top_artist_streams}</strong> cumulative streams across cataloged tracks.</li>
            <li><strong>Market Dominance:</strong> <code>{top_genre_name}</code> represents the largest streaming share in the active filtered view.</li>
            <li><strong>Collaborations Integrity:</strong> All multi-artist tracks have been normalized into primary attribution, ensuring that tracks featuring guest vocalists or producers do not duplicate overall catalog stream counts.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
