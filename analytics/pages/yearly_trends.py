"""
Page 4: Yearly Music Trends for Spotify Trends Analytics Studio.
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
from analytics.components.charts import create_line_chart, create_vertical_bar_chart
from analytics.utils.queries import get_yearly_cohort_summary
from analytics.utils.formatting import format_number


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Yearly Music Trends",
        subtitle="Catalog analysis across release-year cohorts and musical evolution.",
        metadata=metadata
    )

    # Crucial Analytic Boundary Notice
    notice_html = (
        f'<div style="background:#181818;border:1px solid #333333;border-left:3px solid #38bdf8;border-radius:6px;padding:8px 12px;margin-bottom:12px;font-size:0.8rem;color:#CCCCCC;">'
        f'<strong style="color:#38bdf8;">ANALYTIC NOTICE:</strong> '
        f'Charts illustrate <strong>release-year cohort trends</strong> (tracks by original publication year). '
        f'They do <em>not</em> represent historical annual stream growth, as snapshots reflect cumulative streams.'
        f'</div>'
    )
    st.markdown(notice_html, unsafe_allow_html=True)

    if df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    yearly = get_yearly_cohort_summary(df)
    if yearly.empty:
        st.info("No release-year data available for current selection.")
        return

    # 1. Yearly KPIs
    oldest_year = int(yearly["release_year"].min())
    latest_year = int(yearly["release_year"].max())
    peak_release_year = int(yearly.sort_values(by="track_count", ascending=False).iloc[0]["release_year"])
    peak_tracks = int(yearly["track_count"].max())

    render_kpi_row([
        {"title": "Release Era", "value": f"{oldest_year} - {latest_year}", "subtitle": "Year span"},
        {"title": "Peak Catalog Year", "value": str(peak_release_year), "subtitle": f"{peak_tracks} tracks released"},
        {"title": "Avg Popularity Trend", "value": f"{yearly['popularity'].iloc[-1]:.1f}/100", "subtitle": f"Latest cohort ({latest_year})"},
        {"title": "Total Cohort Streams", "value": format_number(yearly["streams"].sum()), "subtitle": "All release cohorts"}
    ])

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. Charts: Releases and Popularity by Year
    col_vol, col_pop = st.columns(2)

    with col_vol:
        st.markdown("### Tracks by Release Year")
        fig_vol = create_vertical_bar_chart(
            yearly,
            x_col="release_year",
            y_col="track_count",
            title="Catalog Track Volume by Release Year"
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with col_pop:
        st.markdown("### Average Popularity by Release Year")
        fig_pop = create_line_chart(
            yearly,
            x_col="release_year",
            y_col="popularity",
            title="Cohort Mean Popularity (0-100)",
            line_color="#1DB954"
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Acoustic Evolution Over Time
    st.markdown("### Acoustic Feature Evolution Across Release Eras")
    audio_features = [f for f in ["danceability", "energy", "acousticness", "valence"] if f in yearly.columns]
    
    if len(audio_features) >= 2:
        import plotly.graph_objects as go
        fig_features = go.Figure()
        colors = {"danceability": "#1DB954", "energy": "#38bdf8", "acousticness": "#f59e0b", "valence": "#ec4899"}
        
        for feat in audio_features:
            fig_features.add_trace(go.Scatter(
                x=yearly["release_year"],
                y=yearly[feat],
                mode="lines+markers",
                name=feat.capitalize(),
                line=dict(width=2.2, color=colors.get(feat, "#ffffff")),
                marker=dict(size=5)
            ))

        fig_features.update_layout(
            paper_bgcolor="#121212",
            plot_bgcolor="#181818",
            title=dict(text="Mean Normalized Feature Values (0.0 to 1.0) Over Time", font=dict(color="#FFFFFF", size=13)),
            font=dict(color="#B3B3B3", size=11),
            xaxis=dict(gridcolor="#282828", automargin=True, tickfont=dict(size=10)),
            yaxis=dict(gridcolor="#282828", range=[0, 1], automargin=True, tickfont=dict(size=10)),
            margin=dict(l=20, r=20, t=35, b=25),
            height=300,
            autosize=True
        )
        st.plotly_chart(fig_features, use_container_width=True)
