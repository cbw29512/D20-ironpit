from __future__ import annotations

from app.content.monster_aura_source import (
    fire_aura_source_is_fully_modeled,
    source_end_turn_damage_auras,
    source_roll_advantage_auras,
    source_start_turn_condition_auras,
)
from app.domain.models import CombatantTemplate


def aura_trait_issues(
    template: CombatantTemplate, row: dict[str, object], expected: list[str],
) -> tuple[list[str], set[str]]:
    issues: list[str] = []
    certified: set[str] = set()
    if "Fire Aura" in expected:
        source_auras = source_end_turn_damage_auras(template.name)
        if template.end_turn_damage_auras != source_auras:
            issues.append("trait-runtime-mismatch:fire-aura")
        elif not fire_aura_source_is_fully_modeled(row):
            issues.append("trait-unmodeled-clause:fire-aura")
        else:
            certified.add("Fire Aura")
    source_start = source_start_turn_condition_auras(template.name)
    if source_start:
        if template.start_turn_save_condition_auras != source_start:
            issues.append("trait-runtime-mismatch:start-turn-condition-aura")
        else:
            certified.update(aura.name for aura in source_start)
    source_roll = source_roll_advantage_auras(template.name)
    if source_roll:
        if template.roll_advantage_auras != source_roll:
            issues.append("trait-runtime-mismatch:roll-advantage-aura")
        else:
            certified.update(aura.name for aura in source_roll)
    return issues, certified
