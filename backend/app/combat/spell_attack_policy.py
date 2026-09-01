from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction


@dataclass(frozen=True)
class SpellAttackChoice:
    action: SpellAttackAction
    target: EncounterCombatant


def _slot_available(caster: EncounterCombatant, action: SpellAttackAction, turn_key: str) -> bool:
    if action.level == 0:
        return True
    if not slot_spell_available(caster.state, turn_key):
        return False
    return any(
        item.id == f"spell-slot-{action.level}" and item.current_uses > 0
        for item in caster.state.resources
    )


def choose_spell_attack(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> SpellAttackChoice | None:
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    indexed = list(enumerate(caster.state.template.spell_attack_actions))
    for _, action in sorted(indexed, key=lambda item: (-item[1].level, item[0])):
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            continue
        if not _slot_available(caster, action, turn_key):
            continue
        legal = [
            target for target in enemies
            if target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
            and combatant_distance(caster, target) <= action.range_ft
        ]
        target = min(
            legal,
            key=lambda member: (combatant_distance(caster, member), member.combatant_id),
            default=None,
        )
        if target is not None:
            return SpellAttackChoice(action, target)
    return None
