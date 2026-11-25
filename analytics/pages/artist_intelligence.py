"""
Page 2: Artist Intelligence for Spotify Trends Analytics Studio.
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
from analytics.components.charts import create_horizontal_bar_chart, create_radar_chart
from analytics.utils.queries import get_top_artists_by_streams
from analytics.utils.formatting import format_number, format_duration


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Artist Intelligence",
        subtitle="Individual artist metrics, discography breakdown, and primary attribution performance.",
        metadata=metadata
    )

    if df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    # 1. Top Artists Table & Chart
    top_artists = get_top_artists_by_streams(df, limit=15)
    
    col_chart, col_rank = st.columns([1, 1])
    with col_chart:
        st.markdown("### Top Ranked Artists (Uniquely Attributed Streams)")
        if not top_artists.empty:
            fig = create_horizontal_bar_chart(
                top_artists.head(10),
                x_col="total_streams",
                y_col="primary_artist_name",
                title="Top 10 Artists by Primary Streams"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_rank:
        st.markdown("### Primary vs. Credited Streams Rule")
        proto_html = (
            f'<div style="background:#181818;border:1px solid #282828;border-radius:8px;padding:12px 14px;font-size:0.82rem;color:#CCCCCC;line-height:1.5;">'
            f'<span style="color:#1DB954;font-weight:700;">COLLABORATION INTEGRITY PROTOCOL:</span> '
            f'When tracks feature multiple collaborators (e.g. <em>Artist A feat. Artist B</em>), '
            f'the pipeline strictly attributes the track\'s stream total to the <strong>primary lead artist</strong> '
            f'to prevent double-counting. Credited featured artists are mapped in <code>track_artists</code> junction.'
            f'</div>'
        )
        st.markdown(proto_html, unsafe_allow_html=True)

        if not top_artists.empty:
            st.markdown("#### Artist Leaderboard")
            display_df = top_artists.copy()
            display_df["Streams"] = display_df["total_streams"].apply(format_number)
            display_df = display_df.rename(columns={
                "primary_artist_name": "Artist",
                "track_count": "Tracks",
                "avg_popularity": "Avg Popularity"
            })[["Artist", "Tracks", "Streams", "Avg Popularity"]]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid #282828; margin: 16px 0;'>", unsafe_allow_html=True)

    # 2. Artist Deep Dive Explorer
    st.markdown("### Artist Deep Dive")
    all_artists = sorted([a for a in df["primary_artist_name"].unique() if a and a != "Unknown Artist"])

    if all_artists:
        selected_artist = st.selectbox("Select Artist to Inspect", all_artists)
        artist_tracks = df[df["primary_artist_name"] == selected_artist]

        total_artist_streams = int(artist_tracks["streams"].sum()) if "streams" in artist_tracks.columns else 0
        avg_artist_pop = round(float(artist_tracks["popularity"].mean()), 1) if "popularity" in artist_tracks.columns else 0.0
        primary_genre = artist_tracks["primary_genre"].iloc[0] if "primary_genre" in artist_tracks.columns and not artist_tracks.empty else "N/A"

        render_kpi_row([
            {"title": "Artist", "value": selected_artist, "subtitle": "Selected creator"},
            {"title": "Track Count", "value": str(len(artist_tracks)), "subtitle": "Cataloged releases"},
            {"title": "Attributed Streams", "value": format_number(total_artist_streams), "subtitle": "Cumulative lead streams"},
            {"title": "Market Score", "value": f"{avg_artist_pop}/100", "subtitle": "Mean popularity"},
            {"title": "Signature Genre", "value": primary_genre, "subtitle": "Primary sound"}
        ])

        # Artist Audio Profile Radar
        audio_cols = ["danceability", "energy", "speechiness", "acousticness", "liveness", "valence"]
        available_audio = [c for c in audio_cols if c in artist_tracks.columns]

        col_radar, col_disc = st.columns([1, 1.25])
        with col_radar:
            if available_audio:
                artist_audio_avg = [round(float(artist_tracks[c].mean()), 3) for c in available_audio]
                fig_radar = create_radar_chart(
                    categories=[c.capitalize() for c in available_audio],
                    values=artist_audio_avg,
                    title=f"Audio Signature • {selected_artist}",
                    name=selected_artist
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        with col_disc:
            st.markdown(f"#### Tracks Catalog • {selected_artist}")
            t_cols = ["title", "album_title", "release_date", "streams", "popularity", "duration_ms"]
            avail_t_cols = [c for c in t_cols if c in artist_tracks.columns]
            table_tracks = artist_tracks[avail_t_cols].copy()
            if "streams" in table_tracks.columns:
                table_tracks["streams"] = table_tracks["streams"].apply(format_number)
            if "duration_ms" in table_tracks.columns:
                table_tracks["duration_ms"] = table_tracks["duration_ms"].apply(format_duration)
            st.dataframe(table_tracks, use_container_width=True, hide_index=True)
