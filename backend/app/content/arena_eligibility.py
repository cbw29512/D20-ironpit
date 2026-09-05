from __future__ import annotations

import re

from app.content.movement_modes import parse_movement_profile, source_movement_modes
from app.domain.models import CombatantTemplate
from app.domain.movement import MovementModes

_SPEED_TEXT = re.compile(r"\d+\s*ft\b", re.IGNORECASE)


def _environment_movement(source: object | MovementModes) -> MovementModes:
    if isinstance(source, MovementModes):
        return source
    text = str(source).strip()
    if _SPEED_TEXT.search(text):
        return parse_movement_profile(text)
    return source_movement_modes(text)


def deferred_environment_reason(source: object | MovementModes) -> str | None:
    """Return standard-Iron-Pit environment blockers from movement mechanics, never names."""
    movement = _environment_movement(source)
    if movement.fly_ft > 0:
        return None
    if movement.swim_ft > 0 and movement.walk_ft <= 5:
        return "aquatic-only"
    return None


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    """Ignore movement-only rules; reject creatures that cannot function in the standard arena."""
    if template.kind != "monster":
        return True
    movement = template.movement_modes
    if deferred_environment_reason(movement) is not None:
        return False
    return any((
        movement.walk_ft > 0,
        movement.fly_ft > 0,
        movement.climb_ft > 0,
        movement.swim_ft > 0,
        movement.burrow_ft > 0,
    ))


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [template for template in templates if standard_arena_eligible(template)]
