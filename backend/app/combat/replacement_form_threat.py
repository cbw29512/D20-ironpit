"""Conservative source-grounded single-enemy Action pressure for form AI.

A lookahead heuristic, not combat resolution: one plausible enemy Action and
no dice, movement, resource, or template mutation.
"""
from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.printed_damage import save_mean_damage, weapon_mean_damage
from app.combat.replacement_form_spell_threat import single_enemy_spell_pressure
from app.combat.resources import resource_available
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)


def _can_reach(attack, distance: int, speed: int) -> bool:
    if attack.unavailable_reason is not None:
        return False
    weapon = attack.weapon
    if weapon.attack_kind is WeaponAttackKind.MELEE:
        return distance <= speed + weapon.reach_ft
    return weapon.long_range_ft is not None and distance <= weapon.long_range_ft


def _sequence_pressure(template, available: dict, distance: int, speed: int, state) -> float:
    definition = template.attack_action
    if definition is None:
        return 0.0
    variants = definition.variants or [definition]
    scores = []
    for variant in variants:
        count = (variant.repetitions.dice_count
                 * (variant.repetitions.dice_size + 1) / 2
                 if getattr(variant, "repetitions", None) else 1.0)
        total = 0.0
        for slot in variant.slots:
            weapons = [
                weapon_mean_damage(available[attack_id])
                for attack_id in slot.attack_ids
                if attack_id in available and _can_reach(available[attack_id], distance, speed)
            ]
            saves = [
                save_mean_damage(save)
                for save in template.saving_throw_actions
                if save.id in slot.save_action_ids
                and distance <= save.range_ft + speed
                and resource_available(state, save.resource_id, save.resource_cost)
            ]
            total += max([0.0, *weapons, *saves])
        scores.append(count * total)
    return max(scores, default=0.0)


def single_enemy_pressure(enemy, defender) -> float:
    """Largest plausible *printed* Action damage from one active enemy."""
    try:
        state = enemy.state
        if (state.is_dead or not state.is_alive or state.current_hp <= 0
            or is_incapacitated(state)):
            return 0.0
        template = state.template
        distance = combatant_distance(enemy, defender)
        speed = max(0, template.speed_ft)
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        available = {attack.id: attack for attack in attacks}
        weapons = [
            weapon_mean_damage(attack) for attack in attacks
            if _can_reach(attack, distance, speed)
        ]
        saves = [
            save_mean_damage(save) for save in template.saving_throw_actions
            if distance <= save.range_ft + speed
            and resource_available(state, save.resource_id, save.resource_cost)
        ]
        sequence = _sequence_pressure(template, available, distance, speed, state)
        return max([0.0, *weapons, *saves, sequence])
    except Exception:
        logger.exception("Enemy attack threat estimate failed: %s.", enemy.combatant_id)
        raise


def incoming_attack_pressure(defender, setup) -> float:
    """Highest single-enemy weapon, save or spell exposure; no focus-fire sum."""
    try:
        opponents = setup.monsters if defender.side == "heroes" else setup.heroes
        return max((max(
            single_enemy_pressure(enemy, defender),
            single_enemy_spell_pressure(enemy, defender, setup),
        ) for enemy in opponents), default=0.0)
    except Exception:
        logger.exception("Incoming attack pressure failed for %s.", defender.combatant_id)
        raise


def pressure_may_be_lethal(current_hp: float, temporary_hp: float, pressure: float) -> bool:
    return current_hp > 0 and pressure > 0 and pressure >= current_hp + max(0, temporary_hp)
