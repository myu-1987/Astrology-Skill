"""Adapter around the `jyotishganit` library: D1-D60 divisional charts,
Panchanga, Ashtakavarga, Shadbala, and 3-level Vimshottari Dasha.

jyotishganit computes True Chitra Paksha ayanamsa from Spica's live apparent
position, which requires downloading the JPL DE421 ephemeris and the
Hipparcos star catalog on first use (cached afterwards under the OS's
per-user data directory). Both downloads need outbound internet access the
first time any script runs; see references/known-limitations.md.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _import_jyotishganit():
    try:
        import jyotishganit
    except ImportError as exc:
        raise RuntimeError(
            "jyotishganit is not installed. Run: pip install -r requirements.txt "
            "(from the astrology-ai/ skill directory)."
        ) from exc
    return jyotishganit


def generate_natal_data(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    place_name: str | None = None,
    person_name: str | None = None,
) -> dict[str, Any]:
    """Returns jyotishganit's native JSON structure for a birth/snapshot
    moment: ayanamsa, panchanga, d1Chart, divisionalCharts, ashtakavarga,
    dashas. Raises RuntimeError with an actionable message on the two most
    common first-run failures (ephemeris/star-catalog download)."""
    jyotishganit = _import_jyotishganit()
    try:
        chart = jyotishganit.calculate_birth_chart(
            birth_dt,
            latitude,
            longitude,
            tz_offset_hours,
            place_name,
            person_name,
        )
    except OSError as exc:
        raise RuntimeError(
            "jyotishganit could not download required astronomical data "
            "(JPL ephemeris and/or the Hipparcos star catalog, needed once per "
            "machine). This needs outbound internet access on first run; if "
            "you're behind a firewall, allow access to ssd.jpl.nasa.gov and "
            "cdsarc.cds.unistra.fr, or run this once from an unrestricted "
            f"network. Original error: {exc}"
        ) from exc
    return jyotishganit.get_birth_chart_json(chart)


def extract_ascendant(d1_chart: dict[str, Any]) -> dict[str, Any] | None:
    """House 1 of the D1 chart doubles as the Ascendant/Lagna; pull out a
    flat convenience summary (sign, degree-in-sign, nakshatra, pada)."""
    houses = d1_chart.get("houses", [])
    house1 = next((h for h in houses if h.get("number") == 1), None)
    if house1 is None:
        return None
    return {
        "sign": house1.get("sign"),
        "degrees": house1.get("signDegrees"),
        "nakshatra": house1.get("nakshatra"),
        "pada": house1.get("pada"),
        "nakshatra_deity": house1.get("nakshatraDeity"),
    }
