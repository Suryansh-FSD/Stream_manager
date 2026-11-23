"""
Custom styled KPI Metric Cards for Spotify Trends Analytics Studio.
Renders dark charcoal cards with elevated borders, green accents, and micro-typography.
"""
from typing import Optional, List, Dict, Any
import streamlit as st


def render_metric_card(
    title: str, 
    value: str, 
    subtitle: Optional[str] = None, 
    delta: Optional[str] = None,
    delta_positive: bool = True
) -> None:
    """Renders a single premium Spotify-inspired dark KPI card."""
    delta_html = ""
    if delta:
        delta_color = "#1DB954" if delta_positive else "#ef4444"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f"""
        <span style="color: {delta_color}; font-size: 0.8rem; font-weight: 600; margin-left: 8px;">
            {arrow} {delta}
        </span>
        """

    sub_html = f"""<div style="color: #888888; font-size: 0.75rem; margin-top: 4px;">{subtitle}</div>""" if subtitle else ""

    card_html = f"""
    <div style="
        background: #181818;
        border: 1px solid #282828;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 12px;
    ">
        <div style="color: #B3B3B3; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px;">
            {title}
        </div>
        <div style="display: flex; align-items: baseline; margin-top: 8px;">
            <div style="color: #FFFFFF; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.5px;">
                {value}
            </div>
            {delta_html}
        </div>
        {sub_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_row(metrics: List[Dict[str, Any]]) -> None:
    """Renders a responsive horizontal grid of KPI metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            render_metric_card(
                title=m["title"],
                value=m["value"],
                subtitle=m.get("subtitle"),
                delta=m.get("delta"),
                delta_positive=m.get("delta_positive", True)
            )
