"""Loading and saving chart JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _json_default(obj: Any) -> Any:
    # numpy scalars (e.g. np.float64 from jyotishganit's Skyfield-backed math)
    # aren't JSON-serializable directly; unwrap to a native Python value
    # instead of stringifying them, so downstream numeric comparisons work.
    item = getattr(obj, "item", None)
    if callable(item):
        return item()
    return str(obj)


def save_chart(data: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_json_default, ensure_ascii=False)
    return out_path


def load_chart(chart_path: str | Path) -> dict[str, Any]:
    path = Path(chart_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Chart file not found: {path}. Generate one first with generate_chart.py "
            f"or generate_horary.py."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
