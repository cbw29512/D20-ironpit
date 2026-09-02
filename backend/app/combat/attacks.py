from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated, extend_rage_from_attack
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import apply_hit_conditions, attack_roll_condition_sources
from app.combat.damage import BonusDamageSpec, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.graze import resolve_graze_miss
from app.combat.modifier_stack import (
    apply_d20_bonus_dice, attacks_against_advantage_sources, consume_attacks_against_advantage,
    consume_next_attack_against_advantage, effective_armor_class, next_attack_against_advantage_sources,
)
from app.combat.parry import resolve_parry_hit
from app.combat.range import resolve_attack_roll_mode
from app.combat.reckless_attack import attacks_against_reckless_advantage, reckless_attack_advantage
from app.combat.rolls import roll_d20
from app.combat.sap import apply_weapon_sap, consume_sap, sap_disadvantage
from app.combat.tactical_master import apply_tactical_master_sap
from app.combat.vex import apply_vex_mastery
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, CombatantState, WeaponAttack
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


def resolve_attack(
    sequence: int, round_number: int, attacker: CombatantState, defender: CombatantState,
    attack: WeaponAttack, distance_ft: int, dice: DiceProvider,
    actor_event_id: str | None = None, target_event_id: str | None = None,
    spend_action: bool = True, advantage_sources: int = 0, other_disadvantage_sources: int = 0,
    feature_id: str | None = None, turn_key: str | None = None, bonus_damage: BonusDamageSpec | None = None,
    close_enemy_active: bool = True, redirect_target: CombatantState | None = None,
    redirect_target_event_id: str | None = None, affected_states: list[CombatantState] | None = None,
    sneak_attack_ally_available: bool = False,
) -> BattleEvent:
    try:
        if spend_action and not is_available(attacker, "action"):
            raise ValueError("Action is not available for an attack.")
        weapon = attack.weapon; defender_event_id = target_event_id or defender.template.id
        attacker_event_id = actor_event_id or attacker.template.id
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(attacker, defender, distance_ft, defender_event_id)
        mode = resolve_attack_roll_mode(
            weapon, distance_ft,
            advantage_sources=(advantage_sources + condition_advantage + bloodied_fury_advantage(attacker, attack)
                               + attacks_against_advantage_sources(defender) + attacks_against_reckless_advantage(defender)
                               + reckless_attack_advantage(attacker, attack)
                               + next_attack_against_advantage_sources(attacker, defender_event_id)),
            other_disadvantage_sources=other_disadvantage_sources + condition_disadvantage + sap_disadvantage(attacker),
            close_enemy_active=close_enemy_active,
        )
        attack_roll = apply_d20_bonus_dice(attacker, ModifierKind.ATTACK_ROLL_BONUS_DIE, roll_d20(dice, attack.attack_bonus, mode), dice)
        consume_next_attack_against_advantage(attacker, defender_event_id); consume_sap(attacker)
        consume_attacks_against_advantage(defender); extend_rage_from_attack(attacker, round_number)
        if spend_action: spend(attacker, "action")
        actual_defender, actual_event_id, redirect_used = defender, defender_event_id, False
        if redirect_target is not None and redirect_target is not defender and defender.template.redirect_attack_reaction is not None and is_available(defender, "reaction"):
            spend(defender, "reaction"); actual_defender = redirect_target
            actual_event_id = redirect_target_event_id or redirect_target.template.id; redirect_used = True
        natural = attack_roll.selected_roll or 0; natural_20 = natural == 20
        expanded_critical = natural >= attacker.template.progression_features.critical_hit_minimum
        target_ac = effective_armor_class(actual_defender)
        hit = natural != 1 and (natural_20 or attack_roll.total >= target_ac)
        hit, parry_used = resolve_parry_hit(actual_defender, attack, attack_roll.total, natural, hit)
        if parry_used: target_ac += actual_defender.template.parry_reaction.ac_bonus
        critical = bool(hit and (expanded_critical or (close_hit_is_automatic_critical(actual_defender) and distance_ft <= 5)))
        hp_before = actual_defender.current_hp; temporary_hp_before = actual_defender.temporary_hp
        death_success_before = actual_defender.death_save_successes; death_failure_before = actual_defender.death_save_failures
        concentration_before = actual_defender.concentration.effect_id if actual_defender.concentration else None
        damage_roll = None; damage_components = []; damage_outcome = None; applied_conditions: list[str] = []
        weapon_sap_applied = False; tactical_sap_applied = False; vex_applied = False
        if hit:
            active_turn_key = turn_key or f"{round_number}:{attacker_event_id}"
            damage_roll, rolled_components = resolve_weapon_damage(
                attacker, attack, dice, critical, mode, active_turn_key, bonus_damage=bonus_damage,
                target=actual_defender, sneak_attack_ally_available=sneak_attack_ally_available,
            )
            applied_total, damage_components = apply_damage_defenses(actual_defender, rolled_components); damage_roll.total = applied_total
            applied_types = {part.damage_type for part in damage_components if part.applied_total > 0}
            damage_outcome = apply_damage(actual_defender, applied_total, critical=critical, damage_types=applied_types, dice=dice, affected_states=affected_states)
            applied_conditions = apply_hit_conditions(attack, actual_defender, attacker_event_id, round_number, affected_states)
            weapon_sap_applied = apply_weapon_sap(attacker, attacker_event_id, actual_defender, attack, round_number)
            if not weapon_sap_applied:
                tactical_sap_applied = apply_tactical_master_sap(attacker, attacker_event_id, actual_defender, attack, round_number)
            vex_applied = apply_vex_mastery(attacker, attacker_event_id, actual_event_id, attack, round_number, applied_total)
            end_rage_if_incapacitated(actual_defender)
        else:
            graze = resolve_graze_miss(attacker, actual_defender, attack, dice, affected_states)
            if graze is not None:
                damage_roll, damage_components, damage_outcome = graze
                end_rage_if_incapacitated(actual_defender)
        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker.template.name}: {outcome} with {weapon.name}."
        if not hit and damage_roll is not None:
            description += f" Graze deals {damage_roll.total} {weapon.damage_type.value} damage."
        if redirect_used: description += f" {defender.template.name} uses Redirect Attack; {actual_defender.template.name} becomes the target."
        if parry_used: description += f" {actual_defender.template.name} uses Parry."
        if weapon_sap_applied: description += f" Sap mastery affects {actual_defender.template.name}."
        if tactical_sap_applied: description += f" Tactical Master applies Sap to {actual_defender.template.name}."
        if vex_applied: description += f" Vex primes the next attack against {actual_defender.template.name}."
        if damage_outcome == "relentless_endurance": description += f" {actual_defender.template.name} uses Relentless Endurance and remains at 1 HP."
        if damage_outcome == "undead_fortitude": description += f" {actual_defender.template.name} succeeds on Undead Fortitude and remains at 1 HP."
        if "prone" in applied_conditions: description += f" {actual_defender.template.name} is knocked Prone."
        if "grappled" in applied_conditions: description += f" {actual_defender.template.name} is Grappled."
        if "restrained" in applied_conditions: description += f" {actual_defender.template.name} is Restrained while Grappled."
        if "poisoned" in applied_conditions: description += f" {actual_defender.template.name} is Poisoned."
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack", actor_id=attacker_event_id, actor_name=attacker.template.name,
            target_id=actual_event_id, target_name=actual_defender.template.name, attack_name=weapon.name, target_ac=target_ac,
            attack_roll=attack_roll, damage_roll=damage_roll, damage_components=damage_components, applied_condition_ids=applied_conditions,
            hit=hit, critical=critical, hp_before=hp_before, hp_after=actual_defender.current_hp,
            temporary_hp_before=temporary_hp_before, temporary_hp_after=actual_defender.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=actual_defender.death_save_successes, death_save_failures=actual_defender.death_save_failures,
            is_stable=actual_defender.is_stable, is_dead=actual_defender.is_dead, weapon_id=weapon.id, projectile=weapon.projectile,
            feature_id=feature_id, concentration_ended_effect_id=concentration_before if concentration_before and actual_defender.concentration is None else None,
            animation=weapon.animation, description=description,
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
