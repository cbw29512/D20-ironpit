from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.spell_slot_selection import lowest_available_spell_slot
from app.domain.automatic_damage_spells import AutomaticDamageSpellAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons import DamageType


@dataclass(frozen=True)
class AutomaticDamageSpellChoice:
    action: AutomaticDamageSpellAction
    target: EncounterCombatant
    slot_level: int
    expected_damage: float


def _damage_factor(target: EncounterCombatant, damage_type: DamageType) -> float:
    state = target.state
    if damage_type in state.template.damage_immunities:
        return 0.0
    factor = 1.0
    if damage_type in {*state.template.damage_resistances, *state.temporary_damage_resistances}:
        factor *= 0.5
    if damage_type in state.template.damage_vulnerabilities:
        factor *= 2.0
    return factor


def choose_automatic_damage_spell(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> AutomaticDamageSpellChoice | None:
    if not is_available(caster.state, "action"):
        return None
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    choices: list[tuple[float, int, int, str, AutomaticDamageSpellChoice]] = []
    for action in caster.state.template.automatic_damage_spell_actions:
        slot = lowest_available_spell_slot(caster.state, action.level, turn_key)
        if slot is None:
            continue
        slot_level, _ = slot
        projectiles = action.projectile_count(slot_level)
        mean = projectiles * (
            action.damage_dice_count_per_projectile * (action.damage_dice_size + 1) / 2
            + action.damage_bonus_per_projectile
        )
        for target in enemies:
            if not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0:
                continue
            if combatant_distance(caster, target) > action.range_ft:
                continue
            score = mean * _damage_factor(target, DamageType(action.damage_type))
            choice = AutomaticDamageSpellChoice(action, target, slot_level, score)
            choices.append((score, -slot_level, -target.state.current_hp, target.combatant_id, choice))
    return max(choices, key=lambda item: item[:4])[4] if choices else None
