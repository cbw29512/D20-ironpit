from __future__ import annotations

from app.domain.models import CombatantTemplate
from app.domain.movement import MovementModes


def deferred_environment_reason(source: object | MovementModes) -> str | None:
    """Return standard-arena environment blockers.

    The Iron Pit magically sustains creatures that normally depend on water or
    another breathing environment. Water dependence is therefore environmental,
    not combat math, and never blocks a creature from entering the arena.
    """
    return None


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    """Ignore environment/movement-only rules while requiring some movement mode."""
    if template.kind != "monster":
        return True
    movement = template.movement_modes
    return any((
        movement.walk_ft > 0,
        movement.fly_ft > 0,
        movement.climb_ft > 0,
        movement.swim_ft > 0,
        movement.burrow_ft > 0,
    ))


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [template for template in templates if standard_arena_eligible(template)]
