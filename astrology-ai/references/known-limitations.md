# Known limitations

Read this before trusting an edge case. Everything here was found by actually
installing and running the underlying libraries during this skill's own
development, not inferred from their docs alone.

## jyotishganit (general engine)

- **Pinned to `0.1.7`.** This library has had breaking changes to chart/dasha
  output between 0.1.5, 0.1.6, and 0.1.7. Re-run `tests/` before bumping it.
- **Ayanamsa is fixed** to True Chitra Paksha (computed live from Spica's
  apparent position) with no override in the public API.
- **First run needs internet access** to two hosts: `ssd.jpl.nasa.gov`-family
  mirrors for the JPL DE421 ephemeris, and `cdsarc.cds.unistra.fr` for the
  Hipparcos star catalog (used only to locate Spica for the ayanamsa). Both
  are cached afterwards in a per-user data directory (`%LOCALAPPDATA%\jyotishganit`
  on Windows, `~/Library/Application Support/jyotishganit` on macOS,
  `$XDG_DATA_HOME/jyotishganit` on Linux) - subsequent runs work offline.
  **The Hipparcos host specifically was unreachable from this project's own
  sandboxed development environment** even though PyPI and JPL were fine -
  if `generate_chart.py` fails on first run with a download error, this is
  the most likely cause; try again from a network without that restriction.
- **Timezone is a plain UTC-offset float** (e.g. `5.5`), not an IANA zone
  name - there is no DST handling. Pick the offset that was actually in
  effect at the birth date/time, which may differ from today's offset for
  that location.
- **D2 (Hora) chart only ever places planets in Cancer or Leo.** This is
  *correct* classical Hora-varga behavior (every D2 chart has only two
  possible rashis by definition), not a bug - despite the library's own
  changelog wording ("D2 only populates 2 of 12 houses") reading like one.
  The D2 house *wheel* itself is still a full 12-sign wheel from the D2
  ascendant; only occupancy is restricted to two signs.
- **Rahu/Ketu use a mean-node approximation**, not the true node position.
- **Mercury's Cheshta Bala** differs from some classical texts by design (a
  documented Seeghrochcha-epoch difference in the library, not a defect in
  our adapter).
- **Divisional charts computed**: D2, D3, D4, D7, D9, D10, D12, D16, D20,
  D24, D27, D30, D40, D45, D60. The classical Shodashvarga set also includes
  D6, D8, and D11, which jyotishganit does not compute - they are simply
  absent from `divisional_charts` in the output.
- **Vimshottari Dasha is computed to 3 levels** (Mahadasha -> Antardasha ->
  Pratyantardasha), confirmed by this project's own test run - secondhand
  docs describing deeper sub-periods as "under development" were outdated
  for this version. No Sookshma/Prana (4th/5th) level is available.

## vedicastro / flatlib (KP layer)

- **Two-step install, in order**: `pip install vedicastro` then
  `pip install git+https://github.com/diliprk/flatlib.git@sidereal#egg=flatlib`.
  PyPI does not resolve the git dependency automatically. Installing vanilla
  PyPI `flatlib` instead of this fork breaks with
  `AttributeError: module 'flatlib.const' has no attribute 'AY_LAHIRI'`.
- **`pyswisseph` (a vedicastro dependency) has no prebuilt Windows wheel** as
  of this writing - `pip install` will try to compile it from source, which
  needs Microsoft C++ Build Tools. On macOS/Linux a C compiler is normally
  already available, so this is mainly a Windows-specific hurdle. This
  project's own adapter (`kp_adapter.py`) was therefore verified by direct
  source inspection of vedicastro's GitHub repository rather than a live
  run on this Windows development machine; `generate_chart.py` degrades
  gracefully (keeps the jyotishganit data, sets `kp_data_error`) if
  vedicastro/flatlib/pyswisseph aren't importable.
- **Timezone handling differs from jyotishganit.** vedicastro auto-detects
  an IANA timezone from latitude/longitude (DST-aware) for its own chart
  math, rather than taking an explicit offset. For most present-day
  locations this agrees with the UTC-offset float used elsewhere in this
  skill; for historical dates with different zone/DST rules the two can
  diverge by the DST amount (commonly one hour).
- **`get_houses_data_from_chart`'s returned field names don't cleanly align
  with the values populated** (confirmed by reading the source: the first
  declared field is `Object` but a house-number value is written there).
  `kp_adapter.py` therefore keys houses by their position in the returned
  list (1st = house 1, ... 12th = house 12) rather than trusting field
  names for that column.
- **KP horary is number-based only.** `vedicastro.horary_chart` has no
  free-text/question-parsing method - `find_exact_ascendant_time` needs an
  explicit horary number (1-249). `generate_horary.py` records `--question`
  for context but the actual KP calculation runs on the number.
- **`find_exact_ascendant_time`'s matching window is narrow** (it looks for
  an ascendant-degree difference between 0.0001 and 0.001) and can return
  `None` for a given day/number/location with no match. `generate_horary.py`
  surfaces this as a clear failure rather than silently retrying with a
  different number, since substituting a different number would misrepresent
  the querent's original horary number.
- **Horary ayanamsa is restricted** to `Krishnamurti` or
  `Krishnamurti_Senthilathiban` (a separate, smaller mapping than the
  7-option `AYANAMSA_MAPPING` used for natal KP charts).
- No `LICENSE` file was found at the vedicastro GitHub repo root despite its
  MIT classifier/badge; worth a quick check if your use case needs airtight
  license provenance.

## General

- **Dasha date formats differ between the two libraries**: jyotishganit uses
  ISO `YYYY-MM-DD`; vedicastro's `compute_vimshottari_dasa` uses `dd-mm-yyyy`.
  `analyze_dasha.py` parses each with its own format rather than assuming
  either is universal - don't compare the raw strings directly if you write
  your own tooling against these files.
- **Two house systems coexist in a merged chart JSON.** KP outputs
  (significators, sublords) use Placidus house cusps, the KP convention.
  Parashara/classical interpretation (`d1_chart`, divisional charts) uses
  whole-sign house occupation. This is intentional (it matches how each
  tradition is actually practiced) but means you should not mix a KP cusp
  sublord with a Parashara whole-sign house number as if they were the same
  kind of "house."
- **No automated yoga (planetary combination) detection.** `interpret_chart.py`
  deliberately does not try to auto-detect Raj Yoga, Gajakesari Yoga, etc. -
  see its module docstring for why. Use `references/yogas.md` plus the raw
  chart JSON to reason about these.
- **`transit.py` and `compatibility.py` (Kuta/Guna matching, Mangal Dosha,
  transit-vs-natal overlay) are not implemented in this version.** Neither
  underlying library computes these natively; they need custom classical-
  rule implementation and are planned for a follow-up pass. Don't invoke
  scripts that don't exist yet - check `scripts/` for what's actually there.
