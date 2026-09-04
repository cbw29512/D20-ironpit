from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_UNMODELED_COMBAT_MATH_RIDERS = (
    (
        "hit-point-maximum-decrease",
        re.compile(r"\bHit Point maximum decreases\b", re.IGNORECASE),
    ),
    (
        "ability-score-decrease",
        re.compile(
            r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+score\s+decreases\b",
            re.IGNORECASE,
        ),
    ),
    (
        "created-combatant",
        re.compile(
            r"\b(?:spirit|corpse|creature)\b[^.]{0,100}\b(?:rises|appears)\s+as\b"
            r"|\bunder\s+(?:its|the\s+[^.]{1,40}[’']s)\s+control\b",
            re.IGNORECASE,
        ),
    ),
)


def unmodeled_combat_math_riders(actions: object) -> list[str]:
    """Return source action riders that alter Iron Pit math but lack runtime semantics."""
    try:
        text = str(actions or "")
        return [
            label
            for label, pattern in _UNMODELED_COMBAT_MATH_RIDERS
            if pattern.search(text)
        ]
    except Exception:
        logger.exception("Failed to inspect monster action boundaries.")
        raise


def action_boundary_issues(row: dict[str, object]) -> list[str]:
    """Fail closed when the source contains an unmodeled combat-math action rider."""
    try:
        return [
            f"unsupported-action-rider:{label}"
            for label in unmodeled_combat_math_riders(row.get("actions", ""))
        ]
    except Exception:
        logger.exception("Monster action boundary audit failed for %s.", row.get("name"))
        raise
