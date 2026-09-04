from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DEFERRED_ENVIRONMENT_MONSTERS = {
    "Killer Whale": "aquatic-only",
}
_WALK_SPEED = re.compile(r"^\s*(\d+)\s*ft\.", re.IGNORECASE)
_MODE_SPEED = re.compile(r"\b(Fly|Swim)\s+(\d+)\s*ft\.", re.IGNORECASE)


def source_environment_reason(speed_text: str) -> str | None:
    """Classify source-only movement that cannot function in the standard flat arena."""
    try:
        text = str(speed_text or "")
        walk_match = _WALK_SPEED.search(text)
        walk_ft = int(walk_match.group(1)) if walk_match else 0
        modes = {name.lower(): int(value) for name, value in _MODE_SPEED.findall(text)}
        if modes.get("fly", 0) > 0:
            return None
        if modes.get("swim", 0) > 0 and walk_ft <= 5:
            return "aquatic-only"
        return None
    except Exception:
        logger.exception("Failed to classify source movement for standard-arena eligibility: %r", speed_text)
        raise


def deferred_environment_reason(name: str, speed_text: str | None = None) -> str | None:
    try:
        source_reason = source_environment_reason(speed_text) if speed_text is not None else None
        return source_reason or _DEFERRED_ENVIRONMENT_MONSTERS.get(name)
    except Exception:
        logger.exception("Failed to derive deferred environment reason for %s.", name)
        raise


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    if template.kind != "monster":
        return True
    movement = template.movement_modes
    if movement.fly_ft > 0:
        return True
    if movement.swim_ft > 0 and movement.walk_ft <= 5:
        return False
    return movement.walk_ft > 0


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [template for template in templates if standard_arena_eligible(template)]
