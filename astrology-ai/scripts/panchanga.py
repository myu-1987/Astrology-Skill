#!/usr/bin/env python3
"""Compute the Panchanga (tithi, nakshatra, yoga, karana, vaara) for a date
and location, or a range of dates for Muhurta (auspicious timing) screening.

Values are computed for the exact date+time given (default: local noon).
Traditional tithi/nakshatra readings are usually quoted for sunrise; pass
--time with the local sunrise if that's what you need. This script does not
compute sunrise itself.

Usage:
    python panchanga.py --lat 28.6139 --lon 77.2090 --tz 5.5 --place "New Delhi"
    python panchanga.py --date 2024-04-15 --lat 13.0827 --lon 80.2707 --tz 5.5
    python panchanga.py --start-date 2024-04-01 --end-date 2024-04-30 \
        --lat 12.9716 --lon 77.5946 --tz 5.5
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _engine import jyotishganit_adapter
from _engine.cli_common import add_location_args

DEFAULT_TIME = "12:00:00"


def panchanga_for(date_str: str, time_str: str, lat: float, lon: float, tz: float, place: str | None) -> dict:
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    natal = jyotishganit_adapter.generate_natal_data(dt, lat, lon, tz, place, None)
    return {"date": date_str, "time": time_str, **natal.get("panchanga", {})}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_location_args(parser, require_date=False)
    parser.add_argument("--start-date", help="YYYY-MM-DD, for a date-range Muhurta scan")
    parser.add_argument("--end-date", help="YYYY-MM-DD, for a date-range Muhurta scan")
    args = parser.parse_args()

    time_str = args.time or DEFAULT_TIME

    if args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        results = []
        day = start
        while day <= end:
            results.append(panchanga_for(day.isoformat(), time_str, args.lat, args.lon, args.tz, args.place))
            day += timedelta(days=1)
        for row in results:
            print(f"{row['date']}  {row.get('vaara', ''):<9} tithi={row.get('tithi','')!s:<20} "
                  f"nakshatra={row.get('nakshatra','')!s:<16} yoga={row.get('yoga','')!s:<12} karana={row.get('karana','')}")
    else:
        date_str = args.date or datetime.now().date().isoformat()
        result = panchanga_for(date_str, time_str, args.lat, args.lon, args.tz, args.place)
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
