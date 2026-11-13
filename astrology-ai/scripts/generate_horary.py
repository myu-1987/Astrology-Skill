#!/usr/bin/env python3
"""Generate a KP horary (Prasna) chart for a yes/no or timing question.

KP horary is inherently *number*-based, not a free-text question parser: the
querent (traditionally) thinks of a number from 1 to 249 at the moment of
asking. --question is recorded for context/interpretation only; --number
drives the actual calculation. If --number is omitted, one is chosen here at
invocation time and reported prominently in the output and on stdout - this
is consistent with the classical practice of a spontaneously-chosen number,
but means the result is not reproducible unless you record the number used.

Requires vedicastro (see requirements.txt) - this script has no fallback
without it, unlike generate_chart.py.

Usage:
    python generate_horary.py --question "Will I get the job?" \
        --lat 19.0760 --lon 72.8777 --tz 5.5 --place "Mumbai"

    python generate_horary.py --question "Should I invest in this business?" \
        --number 137 --date 2024-03-15 --lat 12.9716 --lon 77.5946 --tz 5.5 --place "Bangalore"
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _engine import chart_io
from _engine.chart_builder import assemble_chart
from _engine.cli_common import add_location_args, charts_output_dir, slugify
from _engine.kp_adapter import find_horary_ascendant_time, validate_horary_number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", required=True, help="The question being asked (recorded for context)")
    parser.add_argument("--number", type=int, default=None, help="KP horary number, 1-249; randomly chosen if omitted")
    add_location_args(parser, require_date=False, include_name=False)
    args = parser.parse_args()

    date_str = args.date or datetime.now().date().isoformat()

    horary_number = args.number
    if horary_number is None:
        horary_number = random.randint(1, 249)
        print(f"No --number given; randomly selected KP horary number {horary_number} "
              f"(classical practice: a spontaneously-chosen number). Record this if you "
              f"need to reproduce this result.")
    else:
        validate_horary_number(horary_number)

    match = find_horary_ascendant_time(date_str, args.lat, args.lon, args.tz, horary_number)
    if match is None:
        print(
            f"No exact KP horary ascendant match found for number {horary_number} on {date_str} "
            f"at this location. Try a different number, or a different date.",
            file=sys.stderr,
        )
        sys.exit(1)

    matched_time = match["matched_time"]
    chart = assemble_chart(matched_time, args.lat, args.lon, args.tz, args.place, args.question)
    chart["horary"] = {
        "question": args.question,
        "horary_number": horary_number,
        "matched_ascendant_time": matched_time.isoformat() if hasattr(matched_time, "isoformat") else str(matched_time),
        "query_date": date_str,
    }

    slug = slugify(args.question)
    out_path = charts_output_dir() / f"horary-{slug}-{horary_number}.json"
    chart_io.save_chart(chart, out_path)
    print(f"Horary chart saved to: {out_path}")
    if chart.get("kp_data_error"):
        print(f"Note: KP data unavailable - {chart['kp_data_error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
