"""End-to-end smoke test for generate_chart.py: runs the real jyotishganit
engine (via the Spica fixture in conftest.py) and checks the merged chart
JSON has the documented shape and plausible values. Does not require
vedicastro - kp_data is allowed to be None (adapter degrades gracefully)."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_chart import build_chart  # noqa: E402

VALID_SIGNS = {
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
}


def _sample_args(**overrides):
    defaults = dict(
        date="1990-07-15", time="14:30:00",
        lat=28.6139, lon=77.2090, tz=5.5,
        name="Test Person", place="New Delhi",
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_chart_has_documented_top_level_shape():
    chart = build_chart(_sample_args())
    for key in ("person", "ayanamsa", "d1_chart", "divisional_charts", "panchanga", "dashas", "ashtakavarga"):
        assert key in chart, f"missing top-level key: {key}"


def test_ascendant_is_plausible():
    chart = build_chart(_sample_args())
    ascendant = chart["d1_chart"]["ascendant"]
    assert ascendant is not None
    assert ascendant["sign"] in VALID_SIGNS
    assert 0.0 <= ascendant["degrees"] < 30.0


def test_d1_chart_has_twelve_houses_each_with_a_valid_sign():
    chart = build_chart(_sample_args())
    houses = chart["d1_chart"]["houses"]
    assert len(houses) == 12
    assert {h["number"] for h in houses} == set(range(1, 13))
    assert all(h["sign"] in VALID_SIGNS for h in houses)


def test_divisional_charts_cover_the_documented_vargas():
    chart = build_chart(_sample_args())
    expected = {"d2", "d3", "d4", "d7", "d9", "d10", "d12", "d16", "d24", "d27", "d30", "d60"}
    assert expected.issubset(chart["divisional_charts"].keys())


def test_dasha_tree_is_contiguous_and_three_levels_deep():
    chart = build_chart(_sample_args())
    mahadashas = chart["dashas"]["all"]["mahadashas"]
    assert mahadashas, "expected at least one mahadasha"
    for maha_lord, maha in mahadashas.items():
        maha_start = date.fromisoformat(maha["start"])
        maha_end = date.fromisoformat(maha["end"])
        assert maha_start < maha_end, f"{maha_lord} mahadasha has non-positive duration"
        antardashas = maha.get("antardashas", {})
        assert antardashas, f"{maha_lord} mahadasha has no antardashas"
        for antar_lord, antar in antardashas.items():
            antar_start = date.fromisoformat(antar["start"])
            antar_end = date.fromisoformat(antar["end"])
            assert maha_start <= antar_start <= antar_end <= maha_end
            assert antar.get("pratyantardashas"), f"{maha_lord}/{antar_lord} has no pratyantardashas"


def test_panchanga_has_all_five_limbs():
    chart = build_chart(_sample_args())
    panchanga = chart["panchanga"]
    for limb in ("tithi", "nakshatra", "yoga", "karana", "vaara"):
        assert panchanga.get(limb), f"missing panchanga limb: {limb}"


def test_missing_kp_dependency_degrades_gracefully_instead_of_crashing():
    # Whether or not vedicastro is installed in the environment running this
    # test, build_chart() must not raise - it should either populate kp_data
    # or set kp_data_error, never both None/None nor throw.
    chart = build_chart(_sample_args())
    assert (chart["kp_data"] is not None) or (chart["kp_data_error"] is not None)
