from __future__ import annotations

import logging
import re

from app.domain.movement import MovementModes

logger = logging.getLogger(__name__)
_MODE_FIELDS = {
    "climb": "climb_ft",
    "fly": "fly_ft",
    "swim": "swim_ft",
    "burrow": "burrow_ft",
}
_CHOICE = re.compile(
    r"\b(?P<first>climb|fly|swim|burrow)\s+or\s+"
    r"(?P<second>climb|fly|swim|burrow)\s+"
    r"(?P<speed>\d+)\s*ft\.?\s*\(\s*gm[’']s choice\s*\)",
    re.IGNORECASE,
)


def selected_movement_choice(
    source_speed: object,
    runtime: MovementModes,
) -> tuple[set[str], list[str]]:
    """Validate an immutable runtime selection against a printed GM movement choice."""
    try:
        text = str(source_speed)
        match = _CHOICE.search(text)
        if match is None:
            return set(), []

        first = match.group("first").lower()
        second = match.group("second").lower()
        speed = int(match.group("speed"))
        selected = {
            mode
            for mode in (first, second)
            if getattr(runtime, _MODE_FIELDS[mode]) == speed
        }
        inactive = {
            mode
            for mode in (first, second)
            if getattr(runtime, _MODE_FIELDS[mode]) == 0
        }

        if len(selected) == 1 and len(inactive) == 1:
            return selected, []

        return set(), ["movement-choice-source-unmodeled"]
    except Exception as exc:
        logger.exception("Failed to validate printed GM movement choice %r.", source_speed)
        raise RuntimeError("GM movement choice could not be validated.") from exc
