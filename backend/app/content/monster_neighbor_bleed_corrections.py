from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_CORRECTIONS_PATH = Path(__file__).with_name("data") / "srd_5_2_1_neighbor_bleed_corrections.json"
_DEFAULT_FIELDS = ("actions", "rawText")
_ALLOWED_FIELDS = frozenset({"traits", "actions", "bonusActions", "reactions", "legendaryActions", "rawText"})
_EXPECTED_REVIEWED_CORRECTIONS = 6


def _correction_fields(spec: dict[str, object]) -> tuple[str, ...]:
    raw_fields = spec.get("fields")
    if raw_fields is None:
        return _DEFAULT_FIELDS
    if not isinstance(raw_fields, list) or not raw_fields:
        raise RuntimeError("Neighbor-bleed correction fields must be a non-empty list when supplied.")
    fields = tuple(str(field) for field in raw_fields)
    if len(set(fields)) != len(fields) or any(field not in _ALLOWED_FIELDS for field in fields):
        raise RuntimeError(f"Invalid neighbor-bleed correction fields: {fields!r}")
    return fields


def apply_neighbor_bleed_corrections(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Remove only explicitly reviewed next-monster text accidentally appended by PDF extraction."""
    try:
        specs = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
        if not isinstance(specs, list) or len(specs) != _EXPECTED_REVIEWED_CORRECTIONS:
            raise RuntimeError(
                f"SRD neighbor-bleed correction layer must contain {_EXPECTED_REVIEWED_CORRECTIONS} reviewed records."
            )
        by_id = {str(row["id"]): row for row in rows}
        if len({str(spec["id"]) for spec in specs}) != len(specs):
            raise RuntimeError("SRD neighbor-bleed corrections must have unique ids.")
        for spec in specs:
            if not isinstance(spec, dict):
                raise RuntimeError("Each neighbor-bleed correction must be an object.")
            row_id = str(spec["id"])
            trailing = str(spec["trailing_text"])
            row = by_id.get(row_id)
            if row is None:
                raise RuntimeError(f"Neighbor-bleed correction target is missing: {row_id}")
            for field in _correction_fields(spec):
                text = str(row.get(field, "")).rstrip()
                if not text.endswith(trailing):
                    raise RuntimeError(f"Expected {trailing!r} at end of {row_id}.{field}; source drifted.")
                row[field] = text[: -len(trailing)].rstrip()
        return rows
    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply reviewed SRD neighbor-bleed corrections.")
        raise RuntimeError("SRD neighbor-bleed correction layer failed.") from exc
