"""
Page 5: Audio Feature Analysis for Spotify Trends Analytics Studio.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from analytics.components.header import render_header
from analytics.components.metric_cards import render_kpi_row
from analytics.components.charts import create_radar_chart, create_scatter_plot
from analytics.utils.analytics import AUDIO_FEATURE_COLUMNS, ALL_FEATURE_COLUMNS, get_feature_distribution_stats


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Audio Feature Analysis",
        subtitle="Distribution, acoustic density, and multi-dimensional musical signatures.",
        metadata=metadata
    )

    if df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    # 1. Feature Distribution Cards
    available_audio = [c for c in AUDIO_FEATURE_COLUMNS if c in df.columns]
    if not available_audio:
        st.info("No audio features found in current dataset.")
        return

    # Quick summary of top features
    mean_dance = df["danceability"].mean() if "danceability" in df.columns else 0.0
    mean_energy = df["energy"].mean() if "energy" in df.columns else 0.0
    mean_valence = df["valence"].mean() if "valence" in df.columns else 0.0
    mean_tempo = df["tempo"].mean() if "tempo" in df.columns else 0.0

    render_kpi_row([
        {"title": "Mean Danceability", "value": f"{mean_dance:.2f}", "subtitle": "Rhythmic groove (0-1)"},
        {"title": "Mean Energy", "value": f"{mean_energy:.2f}", "subtitle": "Intensity & power (0-1)"},
        {"title": "Mean Valence", "value": f"{mean_valence:.2f}", "subtitle": "Musical positivity (0-1)"},
        {"title": "Mean Tempo", "value": f"{mean_tempo:.1f} BPM", "subtitle": "Average speed"}
    ])

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Interactive Feature Distribution Selector
    st.markdown("### Audio Feature Distributions")
    selected_feat = st.selectbox(
        "Select Feature to Inspect Distribution",
        options=[f for f in ALL_FEATURE_COLUMNS if f in df.columns],
        index=0
    )

    stats = get_feature_distribution_stats(df, selected_feat)
    col_hist, col_stats = st.columns([2, 1])

    with col_hist:
        fig_hist = px.histogram(
            df,
            x=selected_feat,
            nbins=30,
            color_discrete_sequence=["#1DB954"],
            title=f"Histogram Distribution: {selected_feat.capitalize()}"
        )
        fig_hist.update_layout(
            paper_bgcolor="#121212",
            plot_bgcolor="#181818",
            font=dict(color="#B3B3B3", size=12),
            margin=dict(l=30, r=30, t=50, b=40),
            xaxis=dict(gridcolor="#282828"),
            yaxis=dict(gridcolor="#282828")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_stats:
        st.markdown(f"#### {selected_feat.capitalize()} Summary")
        st.markdown(f"""
        <div style="background: #181818; border: 1px solid #282828; border-radius: 8px; padding: 16px; font-size: 0.9rem; color: #E0E0E0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Mean:</span><strong>{stats.get('mean')}</strong></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Median:</span><strong>{stats.get('median')}</strong></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Std Deviation:</span><strong>{stats.get('std')}</strong></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>Min / Max:</span><strong>{stats.get('min')} / {stats.get('max')}</strong></div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span>IQR (Q75 - Q25):</span><strong>{stats.get('iqr')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Overall Catalog Audio Radar
    st.markdown("### Catalog Audio Fingerprint")
    col_radar, col_scatter = st.columns(2)

    with col_radar:
        radar_means = [round(float(df[c].mean()), 3) for c in available_audio]
        fig_radar = create_radar_chart(
            categories=[c.capitalize() for c in available_audio],
            values=radar_means,
            title="Overall Catalog Audio Radar Profile"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_scatter:
        st.markdown("#### Bivariate Feature Comparison")
        axis_x = st.selectbox("X-Axis Feature", options=available_audio, index=0)
        axis_y = st.selectbox("Y-Axis Feature", options=available_audio, index=1 if len(available_audio) > 1 else 0)

        fig_scatter = create_scatter_plot(
            df,
            x_col=axis_x,
            y_col=axis_y,
            color_col="popularity" if "popularity" in df.columns else None,
            hover_name="title" if "title" in df.columns else None,
            title=f"{axis_x.capitalize()} vs {axis_y.capitalize()}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
