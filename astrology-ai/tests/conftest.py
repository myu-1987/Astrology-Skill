"""Shared pytest fixtures.

jyotishganit computes its ayanamsa from Spica's live apparent position,
which needs a one-time download of the Hipparcos star catalog from
cdsarc.cds.unistra.fr. That host is unreachable from some sandboxed/CI
networks (observed during this project's own development) even though
PyPI and the JPL ephemeris host are fine. Since Spica's catalog position is
effectively fixed on human timescales, tests patch the lookup to its J2000
coordinates instead of depending on that specific host being reachable.
This only affects test runs - end users still get the library's real,
cached-after-first-run download behavior.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _patch_spica_lookup(monkeypatch):
    try:
        from skyfield.api import Star
        import jyotishganit.core.astronomical as astro
    except ImportError:
        pytest.skip("jyotishganit not installed; run: pip install -r requirements.txt")

    def _fake_spica():
        return Star(ra_hours=(13, 25, 11.5793), dec_degrees=(-11, 9, 40.759))

    monkeypatch.setattr(astro, "_get_spica", _fake_spica)
