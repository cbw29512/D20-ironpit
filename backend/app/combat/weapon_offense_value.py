from __future__ import annotations

from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import attack_roll_condition_sources
from app.combat.encounter_targeting import close_ranged_threat_exists
from app.combat.frightened import frightened_d20_disadvantage
from app.combat.modifier_stack import attacks_against_advantage_sources, effective_armor_class
from app.combat.offense_value import _attack_probabilities, _damage_factor, _mean_damage
from app.combat.range import resolve_attack_roll_mode
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons import WeaponAttack


def weapon_attack_expected_damage(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    setup: EncounterSetup,
    distance_ft: int,
) -> float:
    """Expected applied weapon damage at one candidate engagement distance."""
    advantage, disadvantage = attack_roll_condition_sources(
        attacker.state, target.state, distance_ft, target.combatant_id,
    )
    advantage += attacks_against_advantage_sources(target.state)
    disadvantage += frightened_d20_disadvantage(attacker.state, setup)
    mode = resolve_attack_roll_mode(
        attack.weapon,
        distance_ft,
        advantage_sources=advantage,
        other_disadvantage_sources=disadvantage,
        close_enemy_active=close_ranged_threat_exists(attacker, setup),
    )
    hit, critical = _attack_probabilities(
        attacker.state, attack.attack_bonus, effective_armor_class(target.state), mode,
    )
    factor = _damage_factor(target.state, DamageType(attack.weapon.damage_type))
    base = attack.fixed_damage if attack.fixed_damage is not None else _mean_damage(
        attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus,
    )
    normal = base * factor
    crit_base = base if attack.fixed_damage is not None else _mean_damage(
        attack.weapon.dice_count * 2, attack.weapon.dice_size, attack.damage_bonus,
    )
    crit = crit_base * factor
    for rider in attack.on_hit_damage:
        rider_factor = _damage_factor(target.state, DamageType(rider.damage_type))
        normal += _mean_damage(rider.dice_count, rider.dice_size, rider.damage_bonus) * rider_factor
        crit += _mean_damage(rider.dice_count * 2, rider.dice_size, rider.damage_bonus) * rider_factor
    if close_hit_is_automatic_critical(target.state) and distance_ft <= 5:
        critical = hit
    return max(0.0, (hit - critical) * normal + critical * crit)
