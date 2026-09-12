from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.offense_value import spell_attack_expected_damage
from app.combat.spellcasting import spell_action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction


@dataclass(frozen=True)
class SpellAttackChoice:
    action: SpellAttackAction
    target: EncounterCombatant
    expected_damage: float


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
        if not spell_action_resource_available(
            caster.state,
            level=action.level,
            resource_id=action.resource_id,
            resource_cost=action.resource_cost,
            turn_key=turn_key,
        ):
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
    score, _, _, _, action, target = max(candidates, key=lambda item: item[:4])
    return SpellAttackChoice(action, target, score)
