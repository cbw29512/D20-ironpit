from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup


def advantage_sources(
    target: EncounterCombatant,
    setup: EncounterSetup,
    effect_id: str,
) -> int:
    count = 0
    for source in [*setup.heroes, *setup.monsters]:
        if source.state.is_dead or source.state.current_hp <= 0:
            continue
        for aura in source.state.template.save_advantage_auras:
            if aura.effect_id != effect_id or combatant_distance(target, source) > aura.range_ft:
                continue
            eligible = source.combatant_id == target.combatant_id and aura.includes_source
            eligible = eligible or target.state.template.archetype in aura.beneficiary_archetypes
            if eligible:
                count += 1
    return count
