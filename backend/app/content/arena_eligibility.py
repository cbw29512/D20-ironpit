from __future__ import annotations

from app.domain.models import CombatantTemplate


def deferred_environment_reason(name: str) -> None:
    """Environmental requirements never defer a combatant in the magical Iron Pit."""
    return None


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    """Every combatant is environmentally supported without rewriting printed movement data."""
    return True


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return list(templates)
