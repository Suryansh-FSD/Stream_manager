"""
Page 6: Popularity and Correlation for Spotify Trends Analytics Studio.
"""
import streamlit as st
import pandas as pd
from scipy import stats

from analytics.components.header import render_header
from analytics.components.metric_cards import render_kpi_row
from analytics.components.charts import create_heatmap, create_scatter_plot
from analytics.utils.analytics import compute_correlation_matrix, ALL_FEATURE_COLUMNS


def render(df: pd.DataFrame, metadata: dict) -> None:
    render_header(
        title="Popularity & Correlation Analysis",
        subtitle="Statistical correlation matrix and feature relationships with track popularity.",
        metadata=metadata
    )

    # Crucial scientific notice
    st.markdown("""
    <div style="background: #181818; border: 1px solid #333333; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 12px 18px; margin-bottom: 24px; font-size: 0.85rem; color: #CCCCCC;">
        <strong style="color: #f59e0b;">STATISTICAL NOTICE:</strong>
        Correlation reflects observed statistical associations and does <em>not</em> imply causation. 
        Additionally, benchmark synthetic records demonstrate pipeline capabilities and should not be cited as real-world industry conclusions.
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    # 1. Correlation Matrix Heatmap
    st.markdown("### Audio Features & Popularity Correlation Matrix")
    corr_df = compute_correlation_matrix(df)

    if not corr_df.empty:
        fig_heat = create_heatmap(corr_df, title="Pearson Correlation Matrix (r)")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Insufficient numeric features to compute correlation matrix.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 2. Key Popularity Relationships
    st.markdown("### Popularity vs. Key Acoustic Drivers")
    cols_pair = st.columns(2)

    with cols_pair[0]:
        if "energy" in df.columns and "popularity" in df.columns:
            r_energy, p_energy = stats.pearsonr(df["energy"].dropna(), df["popularity"].dropna()) if len(df.dropna(subset=["energy", "popularity"])) > 2 else (0, 1)
            st.markdown(f"#### Popularity vs Energy (r = {r_energy:.2f})")
            fig_scat1 = create_scatter_plot(
                df,
                x_col="energy",
                y_col="popularity",
                title=f"Energy vs Popularity (Pearson r = {r_energy:.2f}, p = {p_energy:.3e})",
                hover_name="title" if "title" in df.columns else None
            )
            st.plotly_chart(fig_scat1, use_container_width=True)

    with cols_pair[1]:
        if "danceability" in df.columns and "popularity" in df.columns:
            r_dance, p_dance = stats.pearsonr(df["danceability"].dropna(), df["popularity"].dropna()) if len(df.dropna(subset=["danceability", "popularity"])) > 2 else (0, 1)
            st.markdown(f"#### Popularity vs Danceability (r = {r_dance:.2f})")
            fig_scat2 = create_scatter_plot(
                df,
                x_col="danceability",
                y_col="popularity",
                title=f"Danceability vs Popularity (Pearson r = {r_dance:.2f}, p = {p_dance:.3e})",
                hover_name="title" if "title" in df.columns else None
            )
            st.plotly_chart(fig_scat2, use_container_width=True)

    # 3. Tempo & Valence vs Popularity
    cols_pair2 = st.columns(2)

    with cols_pair2[0]:
        if "valence" in df.columns and "popularity" in df.columns:
            r_val, _ = stats.pearsonr(df["valence"].dropna(), df["popularity"].dropna()) if len(df.dropna(subset=["valence", "popularity"])) > 2 else (0, 1)
            st.markdown(f"#### Popularity vs Valence (r = {r_val:.2f})")
            fig_scat3 = create_scatter_plot(
                df,
                x_col="valence",
                y_col="popularity",
                title=f"Musical Positivity (Valence) vs Popularity",
                hover_name="title" if "title" in df.columns else None
            )
            st.plotly_chart(fig_scat3, use_container_width=True)

    with cols_pair2[1]:
        if "tempo" in df.columns and "popularity" in df.columns:
            r_tempo, _ = stats.pearsonr(df["tempo"].dropna(), df["popularity"].dropna()) if len(df.dropna(subset=["tempo", "popularity"])) > 2 else (0, 1)
            st.markdown(f"#### Popularity vs Tempo (r = {r_tempo:.2f})")
            fig_scat4 = create_scatter_plot(
                df,
                x_col="tempo",
                y_col="popularity",
                title=f"BPM Tempo vs Popularity",
                hover_name="title" if "title" in df.columns else None
            )
            st.plotly_chart(fig_scat4, use_container_width=True)
