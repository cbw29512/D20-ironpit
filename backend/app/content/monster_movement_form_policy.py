from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_STAT_NEUTRAL_SHAPE_CHANGE = re.compile(
    r"shape-shifts into .*?hybrid.*?or .*?, or it returns to its true .*? form\.\s*"
    r"Its game statistics, other than its size, are the same in each form\.",
    re.IGNORECASE,
)


def form_only_movement_is_arena_neutral(row: dict[str, object]) -> bool:
    """Ignore form-only speed when transformation changes no game statistics except size."""
    try:
        speed = str(row.get("speed", ""))
        bonus_actions = str(row.get("bonusActions", ""))
        has_form_only_speed = bool(re.search(r"\([^)]*\bform\s+only\b[^)]*\)", speed, re.IGNORECASE))
        return has_form_only_speed and _STAT_NEUTRAL_SHAPE_CHANGE.search(bonus_actions) is not None
    except Exception as exc:
        logger.exception("Failed to classify form-only movement policy for %s.", row.get("name"))
        raise RuntimeError("Form-only movement arena policy could not be evaluated.") from exc


__all__ = ["form_only_movement_is_arena_neutral"]
