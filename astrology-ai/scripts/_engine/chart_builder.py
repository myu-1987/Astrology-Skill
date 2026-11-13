"""Merges the jyotishganit (general engine) and vedicastro (KP layer)
adapters into the chart JSON schema documented in SKILL.md. Shared by
generate_chart.py (a given birth moment) and generate_horary.py (a
KP-matched horary moment)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from . import jyotishganit_adapter, kp_adapter


def assemble_chart(
    dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    place: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    natal = jyotishganit_adapter.generate_natal_data(dt, latitude, longitude, tz_offset_hours, place, name)

    try:
        kp_data = kp_adapter.build_kp_data(dt, latitude, longitude)
        kp_error = None
    except RuntimeError as exc:
        # vedicastro/flatlib/pyswisseph may be missing (e.g. no Windows build
        # tools) - still return a usable chart from jyotishganit alone.
        kp_data = None
        kp_error = str(exc)

    d1_chart = natal.get("d1Chart", {})
    return {
        "person": {
            "name": name,
            "birth_date": dt.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": tz_offset_hours,
            "place": place,
        },
        "ayanamsa": natal.get("ayanamsa"),
        "d1_chart": {
            **d1_chart,
            "ascendant": jyotishganit_adapter.extract_ascendant(d1_chart),
        },
        "divisional_charts": natal.get("divisionalCharts"),
        "panchanga": natal.get("panchanga"),
        "dashas": natal.get("dashas"),
        "ashtakavarga": natal.get("ashtakavarga"),
        "kp_data": kp_data,
        "kp_data_error": kp_error,
    }
