"""Adapter around `vedicastro`: KP (Krishnamurthi Paddhati) significators,
RL/NL/SL/SSL sublords, Vimshottari Maha/Bhukti, and number-based KP horary.

Install note: vedicastro needs a forked `flatlib` (sidereal branch) installed
as a *second* pip step - see requirements.txt and
references/known-limitations.md. On Windows, vedicastro's own dependency
`pyswisseph` has no prebuilt wheel and needs Microsoft C++ Build Tools to
compile from source.

Timezone note: vedicastro auto-detects an IANA timezone from latitude/
longitude (DST-aware) for its own chart math, independent of the plain
UTC-offset float used elsewhere in this skill (jyotishganit, and the horary
utc_offset string built from --tz here). For most present-day locations
these agree; for historical dates with different zone/DST rules they can
diverge slightly. See known-limitations.md.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .cli_common import format_utc_offset_string

KP_HORARY_AYANAMSAS = ("Krishnamurti", "Krishnamurti_Senthilathiban")


def _import_vedicastro():
    try:
        from vedicastro.VedicAstro import VedicHoroscopeData
    except ImportError as exc:
        raise RuntimeError(
            "vedicastro (and/or its forked flatlib dependency) is not installed. "
            "Run: pip install -r requirements.txt - this installs vedicastro and "
            "then the required flatlib fork as a separate step. See "
            "references/known-limitations.md if you hit a build error for "
            "pyswisseph (Windows needs Microsoft C++ Build Tools)."
        ) from exc
    return VedicHoroscopeData


def _build_horoscope(
    dt: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "Krishnamurti",
    house_system: str = "Placidus",
):
    VedicHoroscopeData = _import_vedicastro()
    return VedicHoroscopeData(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
        latitude, longitude,
        tz=None,  # auto-detect IANA zone from lat/lon (DST-aware)
        ayanamsa=ayanamsa,
        house_system=house_system,
    )


def _row_to_dict(row) -> dict[str, Any]:
    return dict(row._asdict())


def build_kp_data(
    dt: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "Krishnamurti",
    house_system: str = "Placidus",
) -> dict[str, Any]:
    """Returns KP significators (planet-wise + house-wise ABCD) and
    Vimshottari Maha/Bhukti from vedicastro, for merging into a chart JSON.

    Note: get_houses_data_from_chart's returned rows are consumed by list
    position (house 1..12 in order), not by trusting field names - a source
    inspection found the declared field order doesn't cleanly match the
    values populated for every column. See known-limitations.md.
    """
    horoscope = _build_horoscope(dt, latitude, longitude, ayanamsa, house_system)
    chart = horoscope.generate_chart()
    planets_data = horoscope.get_planets_data_from_chart(chart)
    houses_data = horoscope.get_houses_data_from_chart(chart)

    planet_significators = [
        _row_to_dict(row) for row in horoscope.get_planet_wise_significators(planets_data, houses_data)
    ]
    house_significators = [
        _row_to_dict(row) for row in horoscope.get_house_wise_significators(planets_data, houses_data)
    ]
    dasha = horoscope.compute_vimshottari_dasa(chart)

    cusp_sublords = []
    for position, house_row in enumerate(houses_data, start=1):
        row = _row_to_dict(house_row)
        deg = row.get("LonDecDeg")
        sublord_data = horoscope.get_rl_nl_sl_data(deg) if deg is not None else None
        cusp_sublords.append({"house": position, "degree": deg, **(sublord_data or {})})

    return {
        "ayanamsa": ayanamsa,
        "house_system": house_system,
        "planet_significators": planet_significators,
        "house_significators": house_significators,
        "cusp_sublords": cusp_sublords,
        "vimshottari_maha_bhukti": dasha,
    }


def validate_horary_number(horary_number: int) -> None:
    if not (1 <= horary_number <= 249):
        raise ValueError(f"KP horary number must be between 1 and 249, got {horary_number}.")


def find_horary_ascendant_time(
    date_str: str,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    horary_number: int,
    ayanamsa: str = "Krishnamurti",
) -> dict[str, Any] | None:
    """Scans the given local date for the moment the sidereal Ascendant
    matches the horary number's KP sub-division, using vedicastro's number-
    based KP horary method (there is no free-text/question-based variant in
    the library - see references/known-limitations.md).

    Returns None if no match was found that day (the underlying matching
    window is narrow); callers should surface that plainly rather than
    retrying silently, since silently picking a different day/number would
    misrepresent the querent's original horary number.
    """
    validate_horary_number(horary_number)
    if ayanamsa not in KP_HORARY_AYANAMSAS:
        raise ValueError(f"Horary ayanamsa must be one of {KP_HORARY_AYANAMSAS}, got {ayanamsa!r}.")

    from vedicastro.horary_chart import find_exact_ascendant_time

    year, month, day = (int(part) for part in date_str.split("-"))
    utc_offset_str = format_utc_offset_string(tz_offset_hours)

    result = find_exact_ascendant_time(
        year, month, day, utc_offset_str, latitude, longitude, horary_number, ayanamsa
    )
    if result is None:
        return None
    # The library's own type annotation (-> datetime) doesn't match its real
    # return value, a 3-tuple; unpack defensively rather than trusting it.
    matched_time, _houses_chart, houses_data = result
    return {
        "matched_time": matched_time,
        "houses_data": [_row_to_dict(row) for row in houses_data],
    }
