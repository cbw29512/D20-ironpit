from __future__ import annotations

from app.domain.models import CombatantTemplate

_DEFERRED_ENVIRONMENT_MONSTERS = {
    "Killer Whale": "aquatic-only",
}


def deferred_environment_reason(name: str) -> str | None:
    return _DEFERRED_ENVIRONMENT_MONSTERS.get(name)


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    return template.kind != "monster" or deferred_environment_reason(template.name) is None


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [template for template in templates if standard_arena_eligible(template)]
