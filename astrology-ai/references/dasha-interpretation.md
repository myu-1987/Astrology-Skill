# Dasha interpretation rules

`analyze_dasha.py` gives you the computed period tree (which Mahadasha /
Antardasha / Pratyantardasha lord is running on a date, and what's coming up
in the next year). Turning that into a reading uses these classical
principles.

## Reading a Mahadasha lord

1. The planet's natural significations (see `planetary-dignities.md`).
2. Houses it owns in the natal chart, and their significations
   (`house-significations.md`).
3. Houses it occupies and aspects in D1 - these get activated during its
   period.
4. Its own dignity (exalted/debilitated/own sign/neutral) and Shadbala
   strength (from the chart JSON's `d1_chart.houses[].occupants[].shadbala`)
   - a strong, well-placed lord tends to deliver its significations more
   fully than a weak, poorly-placed one.

## Reading an Antardasha lord

1. Its relationship to the Mahadasha lord: natural friendship/enmity, and
   whether they're connected in the chart (conjunction, mutual aspect, or
   sign exchange). A friendly, connected pair tends to blend their
   significations smoothly; an antagonistic pair can produce more
   conflicted or disruptive results.
2. The Antardasha lord's own significations and house lordships, layered on
   top of the Mahadasha's broader theme - the Mahadasha sets the general
   life chapter, the Antardasha colors it with a more specific flavor.

## Transit overlay (manual, until `transit.py` ships)

Classically, a dasha lord's *transit* position matters alongside its natal
placement: a dasha lord transiting through a favorable house from the Moon
or Lagna (especially 3/6/10/11 - the Upachaya houses) tends to support
positive results; transiting through a dusthana (6/8/12) from the Moon can
coincide with more difficulty. This skill does not yet automate transit
calculation (see `known-limitations.md`) - compute the dasha lord's current
sign with an external ephemeris source or a future version of this skill,
then reason about it relative to the natal Moon/Lagna sign.

## KP-specific dasha judgment

See `kp-judgment-rules.md` for how dasha lords are cross-checked against a
house group's ABCD significators - the KP system places more emphasis on
"is the running dasha lord a significator of the houses in question" than
on the Parashara-style qualitative reading above.
