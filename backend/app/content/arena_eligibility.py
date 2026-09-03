from __future__ import annotations

from app.domain.models import CombatantTemplate

_DEFERRED_ENVIRONMENT_MONSTERS = {
    "Killer Whale": "aquatic-only",
}


def deferred_environment_reason(name: str) -> str | None:
    return _DEFERRED_ENVIRONMENT_MONSTERS.get(name)


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
