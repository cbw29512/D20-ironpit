from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_SENSES = re.compile(r"\bSenses\s+(.+?)(?=\s+Languages\b|\s+CR\b|$)", re.IGNORECASE)
_BLINDSIGHT = re.compile(r"\bBlindsight\s+(\d+)\s*ft\.", re.IGNORECASE)
_TRUESIGHT = re.compile(r"\bTruesight\s+(\d+)\s*ft\.", re.IGNORECASE)


def parse_special_senses(row: dict[str, object]) -> tuple[int, int]:
    """Return source-certified Blindsight and Truesight ranges in feet."""
    try:
        match = _SENSES.search(str(row.get("rawText") or ""))
        if match is None:
            return 0, 0
        senses = match.group(1)
        blind = _BLINDSIGHT.search(senses)
        true = _TRUESIGHT.search(senses)
        return (
            int(blind.group(1)) if blind else 0,
            int(true.group(1)) if true else 0,
        )
    except Exception:
        logger.exception("Failed to parse special senses for %s.", row.get("name", "<unknown>"))
        raise


def complete_monster_special_senses(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    """Attach source-derived sight modes without changing monsters that lack them."""
    try:
        by_name = {str(row["name"]): row for row in load_monster_rows()}
        result: list[CombatantTemplate] = []
        for template in templates:
            row = by_name.get(template.name)
            if row is None:
                result.append(template)
                continue
            blindsight, truesight = parse_special_senses(row)
            result.append(template.model_copy(update={
                "blindsight_ft": blindsight,
                "truesight_ft": truesight,
            }))
        return result
    except Exception:
        logger.exception("Failed to complete monster special-sense profiles.")
        raise
