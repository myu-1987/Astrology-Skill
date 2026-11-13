---
name: astrology-ai
description: Generate and interpret Vedic (Jyotish) astrology birth charts - D1 and 15 divisional (varga) charts, Panchanga, Shadbala, 3-level Vimshottari Dasha, Ashtakavarga, and KP (Krishnamurthi Paddhati) significators/sublords. Also generates KP-style horary (Prasna) charts from a number. Use when the user asks for a birth chart, horoscope, Vedic/Jyotish astrology reading, Panchanga for a date, dasha period analysis, or a KP horary/Prasna chart.
license: MIT
compatibility: Requires Python 3.11+ and pip. Installs jyotishganit and a forked flatlib (sidereal branch, via git) through requirements.txt. Network access needed on first run to download ephemeris/star-catalog data (cached afterwards). On Windows, vedicastro's pyswisseph dependency needs Microsoft C++ Build Tools to compile unless a prebuilt wheel is available.
metadata:
  author: myu-1987 (Mahesh Patil)
  category: astrology
  tags: vedic, astrology, jyotish, kp, horoscope, birth-chart, panchanga, dasha
---

# Vedic Astrology Skill

Generate and interpret Vedic astrology birth charts combining a general
calculation engine (`jyotishganit`) with a KP (Krishnamurthi Paddhati)
specialist layer (`vedicastro`).

## Setup

From this skill's directory:

```bash
pip install -r requirements.txt
```

This is a **two-step install under the hood** - `requirements.txt` lists
`vedicastro` and its required forked `flatlib` (sidereal branch) as separate
entries, since PyPI won't resolve that git dependency automatically.
`jyotishganit`'s first real run downloads ephemeris/star-catalog data
(needs internet once, then cached). If vedicastro/flatlib/pyswisseph aren't
installed or fail to build, `generate_chart.py` still works - it degrades to
jyotishganit-only output and reports why KP data is missing. See
[references/known-limitations.md](references/known-limitations.md) before
debugging an install or output issue - most surprises are already documented
there (D2 chart occupancy, timezone handling differences between the two
libraries, the narrow KP horary match window, etc.).

## Scripts

All scripts live in `scripts/` and are run with `python`.

| Script | Purpose |
|---|---|
| `generate_chart.py` | Full natal chart: D1 + 15 divisional charts, Panchanga, Shadbala, Ashtakavarga, 3-level Vimshottari Dasha, KP significators/sublords |
| `generate_horary.py` | KP horary (Prasna) chart from a question + a 1-249 KP number (auto-chosen if omitted) |
| `panchanga.py` | Panchanga for one date, or a date range for Muhurta screening |
| `analyze_dasha.py` | Which dasha period is running on a date, and upcoming transitions |
| `interpret_chart.py` | Structured KP/Parashara signals for a focus area (career, marriage, health, wealth, education, children) - computation only; write the actual prose yourself using this output plus `references/` |

### Generate a natal chart

```bash
python scripts/generate_chart.py \
  --date "1990-07-15" --time "14:30:00" \
  --lat 28.6139 --lon 77.2090 --tz 5.5 \
  --name "Sample Person" --place "New Delhi"
# Saves to Charts/sample-person-chart.json (or $ASTRO_CHARTS_DIR if set)
```

### Generate a KP horary chart

```bash
python scripts/generate_horary.py --question "Will I get the job?" \
  --lat 19.0760 --lon 72.8777 --tz 5.5 --place "Mumbai"
# Or with an explicit KP number (1-249) and date:
python scripts/generate_horary.py --question "Should I invest in this business?" \
  --number 137 --date "2024-03-15" --lat 12.9716 --lon 77.5946 --tz 5.5 --place "Bangalore"
```

### Panchanga (single date or Muhurta range)

```bash
python scripts/panchanga.py --lat 28.6139 --lon 77.2090 --tz 5.5
python scripts/panchanga.py --start-date "2024-04-01" --end-date "2024-04-30" \
  --lat 12.9716 --lon 77.5946 --tz 5.5
```

### Dasha analysis

```bash
python scripts/analyze_dasha.py --chart "Charts/sample-person-chart.json" --date "2024-03-15"
python scripts/analyze_dasha.py --chart "Charts/sample-person-chart.json" --period next-year
```

### Interpretation signals

```bash
python scripts/interpret_chart.py --chart "Charts/sample-person-chart.json" \
  --focus career --system combined
```

Read the module docstring in `interpret_chart.py` before using it: it
deliberately does *not* auto-detect yogas (Raj Yoga, Gajakesari Yoga, etc.) -
see [references/yogas.md](references/yogas.md) and reason about those
directly from the chart JSON.

## Output format

`generate_chart.py` and `generate_horary.py` write one JSON file with:

```
person            birth/query details (name, datetime, lat/lon/tz, place)
ayanamsa          computed True Chitra Paksha value
d1_chart          houses[] with sign/lord/occupants/shadbala/aspects, plus a flat "ascendant" summary
divisional_charts d2..d60 (see references/divisional-charts.md for which ones)
panchanga         tithi, nakshatra, yoga, karana, vaara
dashas            3-level Vimshottari tree: mahadashas -> antardashas -> pratyantardashas
ashtakavarga      sav (combined) and per-planet bhav tables
kp_data           significators (planet-wise + house-wise ABCD), cusp sublords, KP Maha/Bhukti
kp_data_error     set instead of kp_data if vedicastro/flatlib isn't available
horary            (generate_horary.py only) question, horary_number used, matched ascendant time
```

Generated chart files contain personal birth data - they're gitignored by
default (`Charts/`). Handle them accordingly.

## Where to go for more detail

This file stays intentionally short; the depth lives in `references/`,
loaded only when you need it:

- [references/house-significations.md](references/house-significations.md) - the 12 houses, their meanings, and Kendra/Trikona/Dusthana groupings
- [references/planetary-dignities.md](references/planetary-dignities.md) - benefic/malefic natures, exaltation/debilitation, Neecha Bhanga
- [references/nakshatras.md](references/nakshatras.md) - the 27 nakshatras, their lords, and Vimshottari dasha years
- [references/divisional-charts.md](references/divisional-charts.md) - what each varga (D1-D60) means and which ones this skill computes
- [references/yogas.md](references/yogas.md) - classical planetary combinations (not auto-detected - see above)
- [references/dasha-interpretation.md](references/dasha-interpretation.md) - how to read a Mahadasha/Antardasha lord
- [references/kp-judgment-rules.md](references/kp-judgment-rules.md) - the ABCD significator method, cuspal sublords, and the per-focus house groups `interpret_chart.py` uses
- [references/classical-texts.md](references/classical-texts.md) - source texts, further reading, and ethical guidelines for interpretation
- [references/known-limitations.md](references/known-limitations.md) - everything found by actually running these libraries during development; read this before trusting an edge case

## Ethical guidelines (short version)

Emphasize free will over fatalism, be compassionate especially around
health/relationship/death questions, respect the privacy of birth data, and
acknowledge the real uncertainty in any computed chart (birth time accuracy,
ayanamsa choice, the documented library limitations above). See
[references/classical-texts.md](references/classical-texts.md) for the full
guidelines.
