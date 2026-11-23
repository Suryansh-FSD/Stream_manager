"""
Number, date, and text formatting utilities for Spotify Trends Analytics Studio.
"""
from typing import Optional, Union


def format_number(val: Optional[Union[int, float]]) -> str:
    """Formats large numeric values into human-readable shorthand (B, M, K)."""
    if val is None or (isinstance(val, float) and val != val):
        return "N/A"
    
    num = float(val)
    abs_num = abs(num)
    sign = "-" if num < 0 else ""

    if abs_num >= 1_000_000_000:
        return f"{sign}{abs_num / 1_000_000_000:.2f}B"
    elif abs_num >= 1_000_000:
        return f"{sign}{abs_num / 1_000_000:.1f}M"
    elif abs_num >= 1_000:
        return f"{sign}{abs_num / 1_000:.1f}K"
    elif abs_num.is_integer():
        return f"{sign}{int(abs_num):,}"
    else:
        return f"{sign}{abs_num:.2f}"


def format_duration(duration_ms: Optional[Union[int, float]]) -> str:
    """Formats milliseconds into mm:ss string format."""
    if duration_ms is None or (isinstance(duration_ms, float) and duration_ms != duration_ms):
        return "--:--"
    total_seconds = int(duration_ms // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def format_percentage(val: Optional[Union[int, float]], scale_100: bool = False) -> str:
    """Formats float as percentage string."""
    if val is None or (isinstance(val, float) and val != val):
        return "N/A"
    pct = float(val) * 100 if not scale_100 else float(val)
    return f"{pct:.1f}%"
