"""
Page 4: Yearly Music Trends for Spotify Trends Analytics Studio.
"""
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
    st.markdown("""
    <div style="background: #181818; border: 1px solid #333333; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 12px 18px; margin-bottom: 24px; font-size: 0.85rem; color: #CCCCCC;">
        <strong style="color: #38bdf8;">ANALYTIC NOTICE:</strong>
        The charts below illustrate <strong>release-year cohort trends</strong> (tracks categorized by original publication year). 
        They do <em>not</em> represent historical annual streaming activity or year-by-year listening history, as streaming snapshots reflect cumulative performance.
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

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

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

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
                line=dict(width=2.5, color=colors.get(feat, "#ffffff"))
            ))

        fig_features.update_layout(
            paper_bgcolor="#121212",
            plot_bgcolor="#181818",
            title="Mean Normalized Feature Values (0.0 to 1.0) Over Time",
            font=dict(color="#B3B3B3", size=12),
            xaxis=dict(gridcolor="#282828"),
            yaxis=dict(gridcolor="#282828", range=[0, 1]),
            margin=dict(l=30, r=30, t=50, b=40)
        )
        st.plotly_chart(fig_features, use_container_width=True)
