"""Shared CLI argument handling and small helpers used by every script."""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


def add_location_args(parser: argparse.ArgumentParser, require_date: bool = True, include_name: bool = True) -> None:
    """Add the --date/--time/--lat/--lon/--tz/--place(/--name) options most
    scripts share. Date/time default to "now" when require_date is False.
    include_name=False for scripts (like horary) where a person's name
    doesn't apply."""
    parser.add_argument("--date", help="YYYY-MM-DD (local date)" + ("" if require_date else "; defaults to today"))
    parser.add_argument("--time", help="HH:MM:SS, 24-hour, local time" + ("" if require_date else "; defaults to now"))
    parser.add_argument("--lat", type=float, required=True, help="Latitude in decimal degrees")
    parser.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees")
    parser.add_argument("--tz", type=float, required=True, help="Timezone as UTC offset in hours, e.g. 5.5 for IST")
    parser.add_argument("--place", default=None, help="Place name, for display only")
    if include_name:
        parser.add_argument("--name", default=None, help="Person's name, for display only")


def resolve_datetime(date_str: str | None, time_str: str | None) -> datetime:
    """Parse --date/--time into a naive local datetime, defaulting missing
    pieces to the current moment."""
    now = datetime.now()
    if date_str:
        date_part = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_part = now.date()
    if time_str:
        time_part = datetime.strptime(time_str, "%H:%M:%S").time()
    else:
        time_part = now.time().replace(microsecond=0)
    return datetime.combine(date_part, time_part)


def format_utc_offset_string(tz_offset_hours: float) -> str:
    """Format a numeric UTC offset (5.5) as vedicastro's horary module expects
    it ("+05:30"), matching vedicastro.utils.get_utc_offset's own output format."""
    sign = "+" if tz_offset_hours >= 0 else "-"
    magnitude = abs(tz_offset_hours)
    hours = int(magnitude)
    minutes = int(round((magnitude - hours) * 60))
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{sign}{hours:02d}:{minutes:02d}"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "chart"


def charts_output_dir() -> Path:
    """Resolve the output directory for generated chart JSON, honoring the
    ASTRO_CHARTS_DIR environment variable documented in SKILL.md."""
    configured = os.environ.get("ASTRO_CHARTS_DIR")
    out_dir = Path(configured) if configured else Path.cwd() / "Charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
