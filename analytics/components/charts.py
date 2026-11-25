"""
Plotly Chart Builders with unified dark Spotify styling for Spotify Trends Analytics Studio.
"""
from typing import List, Optional, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Unified Spotify Trends palette
SPOTIFY_GREEN = "#1DB954"
DARK_BG = "#121212"
PANEL_BG = "#181818"
GRID_COLOR = "#282828"
TEXT_COLOR = "#FFFFFF"
MUTED_TEXT = "#B3B3B3"

CHART_PALETTE = [
    "#1DB954", "#38bdf8", "#a855f7", "#f59e0b", "#ec4899",
    "#10b981", "#6366f1", "#f97316", "#14b8a6", "#8b5cf6"
]


def apply_dark_theme(fig: go.Figure, title: str = "", height: Optional[int] = None) -> go.Figure:
    """Applies premium Spotify dark UI theme and calibrated layout sizing to a Plotly figure."""
    layout_dict: Dict[str, Any] = {
        "title": {
            "text": title,
            "font": {"size": 13, "color": TEXT_COLOR, "family": "sans-serif"},
            "x": 0.0,
            "xanchor": "left"
        },
        "paper_bgcolor": DARK_BG,
        "plot_bgcolor": PANEL_BG,
        "font": {"color": MUTED_TEXT, "size": 11},
        "margin": {"l": 15, "r": 15, "t": 35, "b": 25},
        "legend": {
            "font": {"color": TEXT_COLOR, "size": 10},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0
        },
        "hoverlabel": {
            "bgcolor": "#242424",
            "font_size": 11,
            "font_color": TEXT_COLOR,
            "bordercolor": "#333333"
        },
        "autosize": True
    }
    if height:
        layout_dict["height"] = height

    fig.update_layout(**layout_dict)
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont={"color": MUTED_TEXT, "size": 10},
        automargin=True
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont={"color": MUTED_TEXT, "size": 10},
        automargin=True
    )
    return fig


def create_horizontal_bar_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    title: str,
    color_col: Optional[str] = None
) -> go.Figure:
    """Creates a horizontal ranked bar chart."""
    sorted_df = df.sort_values(by=x_col, ascending=True)
    fig = px.bar(
        sorted_df,
        x=x_col,
        y=y_col,
        orientation="h",
        color=color_col or x_col,
        color_continuous_scale=[[0, "#0e4a22"], [1, SPOTIFY_GREEN]],
        title=title
    )
    fig.update_coloraxes(showscale=False)
    fig.update_traces(marker_line_width=0)
    return apply_dark_theme(fig, title, height=310)


def create_vertical_bar_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    title: str,
    color_discrete_sequence: Optional[List[str]] = None
) -> go.Figure:
    """Creates a vertical bar chart."""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color_discrete_sequence=color_discrete_sequence or [SPOTIFY_GREEN],
        title=title
    )
    fig.update_traces(marker_line_width=0)
    return apply_dark_theme(fig, title, height=290)


def create_line_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    title: str,
    line_color: str = SPOTIFY_GREEN
) -> go.Figure:
    """Creates a smooth time-series or trend line chart."""
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        markers=True,
        title=title
    )
    fig.update_traces(
        line=dict(color=line_color, width=2.5),
        marker=dict(size=6, color=TEXT_COLOR, line=dict(width=1.5, color=line_color))
    )
    return apply_dark_theme(fig, title, height=290)


def create_pie_chart(
    df: pd.DataFrame, 
    names_col: str, 
    values_col: str, 
    title: str
) -> go.Figure:
    """Creates a modern donut chart."""
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.45,
        color_discrete_sequence=CHART_PALETTE,
        title=title
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=10))
    return apply_dark_theme(fig, title, height=290)


def create_radar_chart(
    categories: List[str], 
    values: List[float], 
    title: str,
    name: str = "Audio Features"
) -> go.Figure:
    """Creates a polar radar chart for audio feature profiles."""
    cat_closed = categories + [categories[0]]
    val_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=val_closed,
        theta=cat_closed,
        fill="toself",
        fillcolor="rgba(29, 185, 84, 0.25)",
        line=dict(color=SPOTIFY_GREEN, width=2),
        name=name
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_COLOR, tickfont=dict(color=MUTED_TEXT, size=8)),
            angularaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR, size=10)),
            bgcolor=PANEL_BG
        ),
        paper_bgcolor=DARK_BG,
        title=dict(text=title, font=dict(size=13, color=TEXT_COLOR)),
        margin=dict(l=25, r=25, t=35, b=25),
        height=290,
        autosize=True
    )
    return fig


def create_scatter_plot(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    title: str,
    color_col: Optional[str] = None,
    hover_name: Optional[str] = None
) -> go.Figure:
    """Creates an interactive scatter plot with trendline."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        hover_name=hover_name,
        color_continuous_scale=[[0, "#0e4a22"], [1, SPOTIFY_GREEN]],
        title=title,
        opacity=0.75
    )
    fig.update_traces(marker=dict(size=7, line=dict(width=0.5, color="#FFFFFF")))
    return apply_dark_theme(fig, title, height=290)


def create_heatmap(
    corr_df: pd.DataFrame, 
    title: str
) -> go.Figure:
    """Creates a correlation matrix heatmap."""
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Viridis",
        title=title
    )
    fig.update_coloraxes(colorbar=dict(tickfont=dict(color=MUTED_TEXT, size=9), thickness=14))
    return apply_dark_theme(fig, title, height=320)
