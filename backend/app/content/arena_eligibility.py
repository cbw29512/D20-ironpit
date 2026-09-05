from __future__ import annotations

from app.content.movement_modes import parse_movement_profile
from app.domain.models import CombatantTemplate
from app.domain.movement import MovementModes


def deferred_environment_reason(source_speed: object | MovementModes) -> str | None:
    """Return standard-Iron-Pit environment blockers from movement mechanics, never names."""
    movement = source_speed if isinstance(source_speed, MovementModes) else parse_movement_profile(source_speed)
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
