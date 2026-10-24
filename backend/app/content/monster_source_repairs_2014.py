from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).with_name("data") / "srd_5_1_monsters_source_repairs.json"
_ALLOWED_FIELDS = frozenset({"source_traits", "source_actions", "source_reactions"})
_ModelT = TypeVar("_ModelT", bound=BaseModel)


def apply_source_text_repairs_2014(rows: list[_ModelT]) -> list[_ModelT]:
    """Apply explicit source-text corrections before semantic parsing."""
    try:
        payload = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("2014 source repair payload must be an object.")

        by_id = {str(getattr(row, "id")): row for row in rows}
        if len(by_id) != len(rows):
            raise ValueError("2014 source rows must have unique IDs before repair.")

        repaired = list(rows)
        index_by_id = {str(getattr(row, "id")): index for index, row in enumerate(rows)}
        for monster_id, updates in payload.items():
            if monster_id not in by_id:
                raise ValueError(f"2014 source repair references unknown monster {monster_id!r}.")
            if not isinstance(updates, dict) or not updates:
                raise ValueError(f"2014 source repair for {monster_id!r} must contain fields.")
            unknown = set(updates) - _ALLOWED_FIELDS
            if unknown:
                raise ValueError(
                    f"2014 source repair for {monster_id!r} has unsupported fields: {sorted(unknown)}"
                )
            if any(not isinstance(value, str) or not value.strip() for value in updates.values()):
                raise ValueError(f"2014 source repair for {monster_id!r} must use non-empty text.")
            repaired[index_by_id[monster_id]] = by_id[monster_id].model_copy(update=updates)

        return repaired
    except Exception as exc:
        logger.exception("Failed to apply explicit 2014 source-text repairs.")
        raise RuntimeError("2014 source-text repairs could not be applied.") from exc
