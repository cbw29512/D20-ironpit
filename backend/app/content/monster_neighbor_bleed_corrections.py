from __future__ import annotations

import json
from pathlib import Path

_CORRECTIONS_PATH = Path(__file__).with_name("data") / "srd_5_2_1_neighbor_bleed_corrections.json"
_FIELDS = ("actions", "rawText")


def apply_neighbor_bleed_corrections(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Remove only explicitly reviewed next-monster text accidentally appended by PDF extraction."""
    specs = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(specs, list) or len(specs) != 5:
        raise RuntimeError("SRD neighbor-bleed correction layer must contain five reviewed records.")
    by_id = {str(row["id"]): row for row in rows}
    if len({str(spec["id"]) for spec in specs}) != len(specs):
        raise RuntimeError("SRD neighbor-bleed corrections must have unique ids.")
    for spec in specs:
        row_id = str(spec["id"])
        trailing = str(spec["trailing_text"])
        row = by_id.get(row_id)
        if row is None:
            raise RuntimeError(f"Neighbor-bleed correction target is missing: {row_id}")
        for field in _FIELDS:
            text = str(row.get(field, "")).rstrip()
            if not text.endswith(trailing):
                raise RuntimeError(f"Expected {trailing!r} at end of {row_id}.{field}; source drifted.")
            row[field] = text[: -len(trailing)].rstrip()
    return rows
