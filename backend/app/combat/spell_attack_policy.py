from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import spell_attack_expected_damage
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
    candidates: list[tuple[float, int, int, str, SpellAttackAction, EncounterCombatant]] = []
    for index, action in enumerate(caster.state.template.spell_attack_actions):
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            continue
        if not _slot_available(caster, action, turn_key):
            continue
        for target in enemies:
            if (
                not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0
                or combatant_distance(caster, target) > action.range_ft
            ):
                continue
            score = spell_attack_expected_damage(caster, target, action, setup)
            candidates.append((score, -action.level, -target.state.current_hp, target.combatant_id, action, target))
    if not candidates:
        return None
    _, _, _, _, action, target = max(candidates, key=lambda item: item[:4])
    return SpellAttackChoice(action, target)
