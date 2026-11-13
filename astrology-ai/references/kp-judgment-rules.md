# KP (Krishnamurthi Paddhati) judgment rules

## The ABCD significator method

For any house, four tiers of planets are considered its significators, in
descending order of strength:

- **A**: planets occupying that house's own nakshatra's lord's position (i.e.
  planets whose nakshatra lord owns a relevant placement) - the strongest tier.
- **B**: planets occupying the house itself.
- **C**: planets aspecting the house.
- **D**: the house's rasi (sign) lord.

A chart's `kp_data.house_significators` (from `vedicastro`) gives these four
tiers per house directly. `interpret_chart.py`'s KP mode pools tiers A/B/C/D
across a focus area's house group into a single "significator" set per side
(supporting vs opposing) - see below for how those groups are chosen.

## Cuspal sublord

In KP, the sublord of a house's cusp (not just the occupying/aspecting
planets) is considered the final word on whether that house's matter will
manifest - more important than the house's rasi lord. `kp_data.cusp_sublords`
gives each house cusp's RL/NL/SL/SSL (Rasi Lord / Nakshatra Lord / Sub Lord /
Sub-Sub Lord) from vedicastro's 249-subdivision system.

## For any event to manifest (the three-part KP test)

1. **Significators must be present** - the relevant houses for the matter
   must have significators (preferably in tier A or B).
2. **Dasha must be supportive** - the current Mahadasha and/or Antardasha
   lord should itself be a significator of the relevant houses.
3. **Cuspal sublord must promise** - the relevant house's cuspal sublord
   should not itself be a strong significator of the houses that negate the
   matter.

## Per-focus house groups used by `interpret_chart.py`

| Focus | Positive (supporting) houses | Negative (opposing) houses | Why |
|---|---|---|---|
| career | 10, 2, 6, 11 | 12, 8 | 10th = profession itself; 2nd = income/sustenance; 6th = service/daily work; 11th = gains/promotion. 12th = loss of position; 8th = sudden disruption/job loss |
| marriage | 2, 7, 11 | 1, 6, 10 | 7th = the spouse/partnership itself; 2nd = family added by marriage; 11th = fulfillment of the desire. 1st/6th/10th are the classical "negative for marriage" houses (separation/obstacles) |
| health | 1, 8 | 6, 8, 12 | 1st = the body/vitality itself; 8th is listed on both sides because it governs both longevity *and* chronic/sudden conditions - read it carefully, not as purely positive or negative. 6th = disease; 12th = hospitalization/loss of health |
| wealth | 2, 11, 5, 9 | 6, 8, 12 | 2nd/11th = direct wealth/gains houses; 5th = speculative gains; 9th = fortune. 6/8/12 are the classical loss/debt/expense houses |
| education | 4, 5, 9, 2 | 12 | 4th = foundational/early education; 5th = intelligence and learning capacity; 9th = higher education; 2nd = speech/accumulated knowledge. 12th = loss of focus/dropping out |
| children | 5, 9, 2, 11 | 1, 6, 10 | 5th = children directly; 9th (5th from 5th) and 2nd (family) and 11th (fulfillment) support it. 1/6/10 mirror the same "negative" pattern used for marriage in classical KP teaching |

These groupings are a commonly taught starting point, not a rigid universal
rule - some KP teachers vary the secondary houses by case. Treat the
"negative" houses as context to weigh against the "positive" ones, not as an
automatic veto.
