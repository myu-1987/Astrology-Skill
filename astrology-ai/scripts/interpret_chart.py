#!/usr/bin/env python3
"""Surface structured, computed signals for a chart focus area - this script
does deterministic computation, not prose. Hand its JSON output plus the
relevant references/*.md file to an LLM to write the actual interpretation.

Scope (by design, not an oversight):
  - KP mode: aggregates ABCD house significators for the focus area's house
    group (see references/kp-judgment-rules.md for why these houses, per
    house) and checks whether the dasha lord running on --date is among them.
  - Parashara mode: house-lord placement/strength (Shadbala rupas) and a
    simple natural-benefic/malefic occupant count for the same houses.
  - Yoga detection (Gajakesari, Raj Yoga, etc.) is intentionally NOT
    automated here - robustly detecting dozens of classical yoga
    combinations from raw planet positions is its own substantial project.
    references/yogas.md gives the definitions; reasoning over this script's
    chart data to spot them is left to the interpreting agent.

Usage:
    python interpret_chart.py --chart Charts/sample-person-chart.json --focus career --system kp
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _engine.chart_io import load_chart

# Per-focus house groups. "positive" houses support the matter; "negative"
# houses work against it. See references/kp-judgment-rules.md for the
# classical reasoning behind each grouping.
FOCUS_HOUSES = {
    "career": {"positive": [10, 2, 6, 11], "negative": [12, 8]},
    "marriage": {"positive": [2, 7, 11], "negative": [1, 6, 10]},
    "health": {"positive": [1, 8], "negative": [6, 8, 12]},
    "wealth": {"positive": [2, 11, 5, 9], "negative": [6, 8, 12]},
    "education": {"positive": [4, 5, 9, 2], "negative": [12]},
    "children": {"positive": [5, 9, 2, 11], "negative": [1, 6, 10]},
}

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}


def kp_signal(chart: dict, houses: dict) -> dict:
    kp_data = chart.get("kp_data")
    if not kp_data:
        return {"available": False, "reason": chart.get("kp_data_error") or "No KP data in this chart."}

    house_sig_by_number = {row["House"]: row for row in kp_data.get("house_significators", [])}

    def planets_for(house_numbers: list[int]) -> set[str]:
        planets: set[str] = set()
        for number in house_numbers:
            row = house_sig_by_number.get(number)
            if not row:
                continue
            for tier in ("A", "B", "C"):
                value = row.get(tier)
                if isinstance(value, list):
                    planets.update(value)
                elif value:
                    planets.add(value)
            if row.get("D"):
                planets.add(row["D"])
        return planets

    positive_planets = planets_for(houses["positive"])
    negative_planets = planets_for(houses["negative"])
    conflicted = positive_planets & negative_planets

    return {
        "available": True,
        "positive_houses": houses["positive"],
        "negative_houses": houses["negative"],
        "positive_significators": sorted(positive_planets),
        "negative_significators": sorted(negative_planets),
        "conflicted_significators": sorted(conflicted),
    }


def dasha_alignment(chart: dict, kp_result: dict, as_of: str | None) -> dict:
    mahadashas = (chart.get("dashas") or {}).get("all", {}).get("mahadashas", {})
    if not mahadashas or not kp_result.get("available"):
        return {"available": False}

    target = date.fromisoformat(as_of) if as_of else date.today()
    current_maha, current_antar = None, None
    for maha_lord, maha in mahadashas.items():
        if date.fromisoformat(maha["start"]) <= target <= date.fromisoformat(maha["end"]):
            current_maha = maha_lord
            for antar_lord, antar in maha.get("antardashas", {}).items():
                if date.fromisoformat(antar["start"]) <= target <= date.fromisoformat(antar["end"]):
                    current_antar = antar_lord
                    break
            break

    positive = set(kp_result.get("positive_significators", []))
    negative = set(kp_result.get("negative_significators", []))
    running_lords = {lord for lord in (current_maha, current_antar) if lord}

    return {
        "available": True,
        "as_of": target.isoformat(),
        "mahadasha_lord": current_maha,
        "antardasha_lord": current_antar,
        "running_lords_supporting": sorted(running_lords & positive),
        "running_lords_opposing": sorted(running_lords & negative),
    }


def parashara_signal(chart: dict, houses: dict) -> dict:
    d1_houses = {h["number"]: h for h in (chart.get("d1_chart") or {}).get("houses", [])}

    def summarize(house_numbers: list[int]) -> list[dict]:
        rows = []
        for number in house_numbers:
            house = d1_houses.get(number)
            if not house:
                continue
            occupants = house.get("occupants", []) or []
            benefic_count = sum(1 for o in occupants if o.get("celestialBody") in NATURAL_BENEFICS)
            malefic_count = sum(1 for o in occupants if o.get("celestialBody") in NATURAL_MALEFICS)
            rows.append({
                "house": number,
                "sign": house.get("sign"),
                "lord": house.get("lord"),
                "lord_placed_house": house.get("lordPlacedHouse"),
                "bhava_bala": house.get("bhavaBala"),
                "occupants": [o.get("celestialBody") for o in occupants],
                "benefic_occupants": benefic_count,
                "malefic_occupants": malefic_count,
            })
        return rows

    return {
        "positive_houses": summarize(houses["positive"]),
        "negative_houses": summarize(houses["negative"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chart", required=True, help="Path to a chart JSON generated by generate_chart.py")
    parser.add_argument("--focus", required=True, choices=sorted(FOCUS_HOUSES), help="Life area to analyze")
    parser.add_argument("--system", choices=["kp", "parashara", "combined"], default="combined")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD for dasha alignment; defaults to today")
    args = parser.parse_args()

    chart = load_chart(args.chart)
    houses = FOCUS_HOUSES[args.focus]

    result: dict = {"focus": args.focus, "system": args.system}
    if args.system in ("kp", "combined"):
        kp_result = kp_signal(chart, houses)
        result["kp"] = kp_result
        result["kp_dasha_alignment"] = dasha_alignment(chart, kp_result, args.date)
    if args.system in ("parashara", "combined"):
        result["parashara"] = parashara_signal(chart, houses)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
