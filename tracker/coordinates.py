"""Utilities for parsing and formatting geographic coordinates."""
from __future__ import annotations

import re
from typing import Optional, Tuple

COORDINATE_PATTERN = re.compile(
    r"^\s*\(?\s*([+-]?\d+(?:\.\d+)?)\s*[,;:]\s*([+-]?\d+(?:\.\d+)?)\s*\)?\s*$"
)


def parse_coordinate_pair(value: object) -> Optional[Tuple[float, float]]:
    """Parse strings such as "(12.34, -56.78)" into latitude/longitude floats."""
    if not isinstance(value, str):
        return None

    match = COORDINATE_PATTERN.match(value)
    if not match:
        return None

    try:
        return float(match.group(1)), float(match.group(2))
    except (TypeError, ValueError):
        return None


def format_coordinate_pair(latitude: Optional[float], longitude: Optional[float]) -> str:
    """Return a canonical string representation for admin initial values."""
    if latitude is None or longitude is None:
        return ""
    return f"({latitude}, {longitude})"
