#!/usr/bin/env python3
"""Generate a complete natal Vedic birth chart: D1-D60 divisional charts,
Panchanga, Ashtakavarga, Shadbala, 3-level Vimshottari Dasha (jyotishganit),
plus KP significators and sublords (vedicastro).

Usage:
    python generate_chart.py --date 1990-07-15 --time 14:30:00 \
        --lat 28.6139 --lon 77.2090 --tz 5.5 --name "Sample Person" --place "New Delhi"

Output is written to Charts/<slug>-chart.json (or $ASTRO_CHARTS_DIR if set).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _engine import chart_io
from _engine.chart_builder import assemble_chart
from _engine.cli_common import add_location_args, charts_output_dir, resolve_datetime, slugify


def build_chart(args: argparse.Namespace) -> dict:
    birth_dt = resolve_datetime(args.date, args.time)
    return assemble_chart(birth_dt, args.lat, args.lon, args.tz, args.place, args.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_location_args(parser, require_date=True)
    parser.add_argument("--output", default=None, help="Explicit output file path (overrides the default Charts/ naming)")
    args = parser.parse_args()

    if not args.date or not args.time:
        parser.error("--date and --time are required for a natal chart (use panchanga.py for a date-only query)")

    chart = build_chart(args)

    if args.output:
        out_path = Path(args.output)
    else:
        slug = slugify(args.name or "chart")
        out_path = charts_output_dir() / f"{slug}-chart.json"

    chart_io.save_chart(chart, out_path)
    print(f"Chart saved to: {out_path}")
    if chart.get("kp_data_error"):
        print(f"Note: KP data unavailable - {chart['kp_data_error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
