# Planetary natures and dignities

## Natural benefics / malefics

| Category | Planets | Notes |
|---|---|---|
| Great benefic | Jupiter (Guru) | Strongest natural benefic |
| Lesser benefic | Venus (Shukra) | |
| Conditional benefic | Moon (Chandra) | Classically stronger when waxing; this skill does not model the waxing/waning distinction automatically - treat Moon as a soft benefic by default |
| Conditional benefic | Mercury (Budha) | Classically benefic when alone or with benefics, malefic when conjunct malefics; this skill treats Mercury as a benefic by default (a simplification) |
| Mild malefic | Sun (Surya) | |
| Lesser malefic | Mars (Mangal) | |
| Great malefic | Saturn (Shani) | |
| Shadow/malefic | Rahu, Ketu | Nodal points, treated as malefic |

`interpret_chart.py`'s Parashara mode uses exactly this natural
classification (Jupiter/Venus/Mercury/Moon as benefic; Sun/Mars/Saturn/Rahu/Ketu
as malefic) for its occupant counts - it does not compute functional
benefic/malefic status by ascendant, which depends on which houses a planet
rules for that specific chart. Functional status should be reasoned about
directly from the chart's ascendant sign and each planet's house lordships.

## Exaltation and debilitation (classical, sign-level)

| Planet | Exalted in | Debilitated in | Own signs |
|---|---|---|---|
| Sun | Aries | Libra | Leo |
| Moon | Taurus | Scorpio | Cancer |
| Mars | Capricorn | Cancer | Aries, Scorpio |
| Mercury | Virgo | Pisces | Gemini, Virgo |
| Jupiter | Cancer | Capricorn | Sagittarius, Pisces |
| Venus | Pisces | Virgo | Taurus, Libra |
| Saturn | Libra | Aries | Capricorn, Aquarius |

A planet exactly at a specific degree within its exaltation/debilitation
sign is at its deepest point (e.g. Sun at 10 degrees Aries); the sign-level
table above is the commonly used approximation for general dignity reading.

## Neecha Bhanga (debilitation cancellation)

A debilitated planet's weakness can be cancelled under several classical
conditions, most commonly: the lord of the debilitation sign is in a Kendra
(1/4/7/10) from the Lagna or from the Moon; or the planet that would be
exalted in the debilitation sign's dispositor is itself well placed. When
cancellation applies, the planet can give unusually strong results (Neecha
Bhanga Raja Yoga) - see `yogas.md`.
