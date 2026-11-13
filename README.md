# astrology-ai

An open-source Vedic (Jyotish) astrology [Agent Skill](https://agentskills.io/specification) - generate and interpret complete birth charts, Panchanga, Vimshottari Dasha, Ashtakavarga, and KP (Krishnamurthi Paddhati) significators/sublords, plus KP-style horary (Prasna) charts.

The installable skill lives in [`astrology-ai/`](astrology-ai/) (its folder
name matches the skill's `name` field, as the Agent Skills spec requires).
Everything else in this repo is project-level scaffolding (license, this
README).

## What it computes

- D1 (Rasi) chart plus 15 divisional (varga) charts: D2, D3, D4, D7, D9,
  D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
- Panchanga (tithi, nakshatra, yoga, karana, vaara)
- Shadbala (six-fold planetary strength, with rupas/minimum-requirement
  built in)
- Ashtakavarga (combined and per-planet)
- 3-level Vimshottari Dasha (Mahadasha -> Antardasha -> Pratyantardasha)
- KP significators (ABCD method), cuspal sublords, and number-based KP
  horary (Prasna) charts

Built on [`jyotishganit`](https://pypi.org/project/jyotishganit/) (general
engine, NASA JPL DE421 ephemeris) and
[`vedicastro`](https://pypi.org/project/vedicastro/) (KP specialist layer).
See [`astrology-ai/references/known-limitations.md`](astrology-ai/references/known-limitations.md)
for exactly what each library does and doesn't do, found by actually
installing and running them during this project's development - read it
before filing an issue about unexpected output.

**Not yet implemented** (planned for a follow-up): transit-vs-natal overlay
and Kuta/Guna compatibility matching. Neither underlying library computes
these natively; they need custom classical-rule implementation that didn't
fit this pass's scope.

## Install

### Claude Code

```bash
git clone <this-repo-url>
cp -r astrology-skill/astrology-ai ~/.claude/skills/astrology-ai
cd ~/.claude/skills/astrology-ai && pip install -r requirements.txt
```

(Or point Claude Code at a plugin/marketplace entry for this repo, if
you're distributing it that way - any mechanism that makes `astrology-ai/`
available as a skill directory works, since it's a standard Agent Skill.)

### Codex CLI / Gemini CLI / Cursor / VS Code (and other Agent-Skills-compatible tools)

These tools read the same open [Agent Skills](https://agentskills.io)
format. Copy or symlink `astrology-ai/` into whatever skills/extensions
directory your tool expects (check your tool's own docs for the exact
path - this varies by tool and changes over time), then run
`pip install -r requirements.txt` from inside it.

### Verify the install

```bash
cd astrology-ai
pip install -r requirements.txt
python -m pytest tests/
```

If `vedicastro`/`flatlib`/`pyswisseph` fail to install (common on Windows
without Microsoft C++ Build Tools - see known-limitations.md), the skill
still works: `generate_chart.py` degrades to jyotishganit-only output and
reports what's missing.

## Usage

See [`astrology-ai/SKILL.md`](astrology-ai/SKILL.md) for the full command
reference, output format, and pointers into the `references/` material an
agent should read for deeper interpretation (house significations, yogas,
nakshatras, dasha rules, KP judgment rules, classical texts, and known
limitations).

## License

MIT - see [LICENSE](LICENSE). Third-party dependencies (`jyotishganit`,
`vedicastro`, the forked `flatlib`) carry their own licenses; see
`astrology-ai/references/known-limitations.md` for notes on these.

## Contributing

This is an early, honestly-scoped pass - contributions are welcome,
especially:

- `transit.py` and `compatibility.py` (see "Not yet implemented" above)
- Automated yoga detection for `interpret_chart.py` (currently intentionally
  left to the interpreting agent - see that script's module docstring)
- Fixes or workarounds for anything in `known-limitations.md`

Please run `python -m pytest astrology-ai/tests` and
`agentskills validate astrology-ai` (from the
[`skills-ref`](https://pypi.org/project/skills-ref/) package) before
submitting a change.
