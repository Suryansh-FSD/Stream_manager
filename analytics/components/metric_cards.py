"""
Custom styled KPI Metric Cards for Spotify Trends Analytics Studio.
Renders dark charcoal cards with elevated borders, green accents, and responsive layout.
"""
from typing import Optional, List, Dict, Any
import streamlit as st


def build_metric_card_html(
    title: str, 
    value: str, 
    subtitle: Optional[str] = None, 
    delta: Optional[str] = None,
    delta_positive: bool = True
) -> str:
    """Builds clean HTML for a single KPI card with zero newlines to prevent Markdown code block bugs."""
    delta_html = ""
    if delta:
        delta_color = "#1DB954" if delta_positive else "#ef4444"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<span style="color:{delta_color};font-size:0.75rem;font-weight:700;margin-left:6px;">{arrow} {delta}</span>'

    sub_html = f'<div style="color:#888888;font-size:0.72rem;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{subtitle}</div>' if subtitle else ""

    return (
        f'<div style="background:#181818;border:1px solid #282828;border-radius:8px;padding:12px 14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);display:flex;flex-direction:column;justify-content:space-between;min-width:0;overflow:hidden;">'
        f'<div style="color:#A0A0A0;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{title}</div>'
        f'<div style="display:flex;align-items:baseline;margin-top:6px;overflow:hidden;">'
        f'<div style="color:#FFFFFF;font-size:1.45rem;font-weight:800;letter-spacing:-0.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{value}</div>'
        f'{delta_html}'
        f'</div>'
        f'{sub_html}'
        f'</div>'
    )


def render_metric_card(
    title: str, 
    value: str, 
    subtitle: Optional[str] = None, 
    delta: Optional[str] = None,
    delta_positive: bool = True
) -> None:
    """Renders a single KPI card."""
    card_html = build_metric_card_html(title, value, subtitle, delta, delta_positive)
    if hasattr(st, "html"):
        st.html(card_html)
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_row(metrics: List[Dict[str, Any]]) -> None:
    """
    Renders a responsive CSS Grid of KPI metric cards.
    Uses st.html to directly insert DOM nodes without Markdown parsing.
    """
    cards_html = "".join([
        build_metric_card_html(
            title=m["title"],
            value=m["value"],
            subtitle=m.get("subtitle"),
            delta=m.get("delta"),
            delta_positive=m.get("delta_positive", True)
        )
        for m in metrics
    ])

    min_card_width = "130px" if len(metrics) >= 6 else "150px"
    grid_html = f'<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax({min_card_width}, 1fr));gap:10px;width:100%;margin-bottom:14px;">{cards_html}</div>'
    if hasattr(st, "html"):
        st.html(grid_html)
    else:
        st.markdown(grid_html, unsafe_allow_html=True)


