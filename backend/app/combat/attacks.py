from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attack_ability_effects import effective_attack_bonus, resolve_attack_ability_reduction
from app.combat.attack_description import build_attack_description
from app.combat.attack_max_hp_reduction import resolve_attack_max_hp_reduction
from app.combat.attack_roll_modifiers import (
    consume_next_attack_advantage, consume_next_attack_disadvantage,
    next_attack_advantage_sources, next_attack_disadvantage_sources,
)
from app.combat.attack_save_riders import AttackSaveRiderOutcome, resolve_attack_save_rider
from app.combat.barbarian import end_rage_if_incapacitated, extend_rage_from_attack
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.conditions import apply_hit_conditions, attack_roll_condition_sources
from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.damage import BonusDamageSpec, resolve_weapon_damage
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.graze import resolve_graze_miss
from app.combat.heroic_inspiration import reroll_failed_attack_with_heroic_inspiration
from app.combat.modifier_stack import (
    apply_d20_bonus_dice, attacks_against_advantage_sources, consume_attacks_against_advantage,
    consume_next_attack_against_advantage, effective_armor_class, next_attack_against_advantage_sources,
)
from app.combat.parry import resolve_parry_hit
from app.combat.range import resolve_attack_roll_mode
from app.combat.reckless_attack import attacks_against_reckless_advantage, reckless_attack_advantage
from app.combat.resources import spend_resource
from app.combat.rolls import roll_d20
from app.combat.sap import apply_weapon_sap, consume_sap, sap_disadvantage
from app.combat.state import terminate_turn
from app.combat.studied_attacks import apply_studied_attack_miss
from app.combat.tactical_master import apply_tactical_master_sap
from app.combat.timed_penalties import d20_disadvantage_sources
from app.combat.topple import resolve_topple_hit
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
    sneak_attack_ally_available: bool = False, off_turn: bool = False,
    saving_throw_advantage_sources: int = 0,
) -> BattleEvent:
    try:
        if spend_action and not is_available(attacker, "action"):
            raise ValueError("Action is not available for an attack.")
        if attack.on_hit_saving_throw is not None and attack.weapon.mastery_property == "topple":
            raise ValueError("One attack event cannot audit both Topple and an on-hit saving throw.")
        weapon = attack.weapon; defender_event_id = target_event_id or defender.template.id
        attacker_event_id = actor_event_id or attacker.template.id
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(attacker, defender, distance_ft, defender_event_id)
        strength_penalty = d20_disadvantage_sources(attacker, "strength") if attack.attack_ability == "strength" else 0
        mode = resolve_attack_roll_mode(
            weapon, distance_ft,
            advantage_sources=(advantage_sources + condition_advantage + bloodied_fury_advantage(attacker, attack)
                               + attacks_against_advantage_sources(defender) + attacks_against_reckless_advantage(defender)
                               + reckless_attack_advantage(attacker, attack) + next_attack_advantage_sources(attacker)
                               + conditional_attack_advantage_sources(attack, defender)
                               + next_attack_against_advantage_sources(attacker, defender_event_id)),
            other_disadvantage_sources=(other_disadvantage_sources + condition_disadvantage + sap_disadvantage(attacker)
                                        + strength_penalty + next_attack_disadvantage_sources(attacker)),
            close_enemy_active=close_enemy_active,
        )
        resource_remaining = spend_resource(attacker, attack.resource_id, attack.resource_cost)
        base_roll = roll_d20(dice, effective_attack_bonus(attacker, attack), mode)
        base_roll, heroic_reroll = reroll_failed_attack_with_heroic_inspiration(attacker, base_roll, effective_armor_class(defender), dice)
        attack_roll = apply_d20_bonus_dice(attacker, ModifierKind.ATTACK_ROLL_BONUS_DIE, base_roll, dice)
        consume_next_attack_against_advantage(attacker, defender_event_id); consume_next_attack_advantage(attacker); consume_next_attack_disadvantage(attacker); consume_sap(attacker)
        consume_attacks_against_advantage(defender); extend_rage_from_attack(attacker, round_number)
        if spend_action: spend(attacker, "action")
        actual_defender, actual_event_id, redirect_used = defender, defender_event_id, False
        if redirect_target is not None and redirect_target is not defender and defender.template.redirect_attack_reaction is not None and is_available(defender, "reaction"):
            spend(defender, "reaction"); actual_defender = redirect_target
            actual_event_id = redirect_target_event_id or redirect_target.template.id; redirect_used = True
        natural = attack_roll.selected_roll or 0; natural_20 = natural == 20
        natural_1 = natural == 1; natural_1_ends_turn = natural_1 and not off_turn
        if natural_1_ends_turn:
            terminate_turn(attacker, "iron-pit-natural-1-attack")
        expanded_critical = natural >= attacker.template.progression_features.critical_hit_minimum
        target_ac = effective_armor_class(actual_defender)
        hit = not natural_1 and (natural_20 or attack_roll.total >= target_ac)
        hit, parry_used = resolve_parry_hit(actual_defender, attack, attack_roll.total, natural, hit)
        if parry_used: target_ac += actual_defender.template.parry_reaction.ac_bonus
        critical = bool(hit and (expanded_critical or (close_hit_is_automatic_critical(actual_defender) and distance_ft <= 5)))
        hp_before = actual_defender.current_hp; temporary_hp_before = actual_defender.temporary_hp
        death_success_before = actual_defender.death_save_successes; death_failure_before = actual_defender.death_save_failures
        concentration_before = actual_defender.concentration.effect_id if actual_defender.concentration else None
        damage_roll = None; damage_components = []; damage_outcome = None; max_hp_before = max_hp_after = None; applied_conditions: list[str] = []; topple = None
        hit_save = AttackSaveRiderOutcome()
        weapon_sap_applied = False; tactical_sap_applied = False; vex_applied = False; studied_applied = False
        if hit:
            active_turn_key = turn_key or f"{round_number}:{attacker_event_id}"
            damage_roll, rolled_components = resolve_weapon_damage(
                attacker, attack, dice, critical, mode, active_turn_key, bonus_damage=bonus_damage,
                target=actual_defender, sneak_attack_ally_available=sneak_attack_ally_available,
            )
            applied_total, damage_components = apply_damage_defenses(actual_defender, rolled_components); damage_roll.total = applied_total
            applied_types = {part.damage_type for part in damage_components if part.applied_total > 0}
            damage_outcome = apply_damage(actual_defender, applied_total, critical=critical, damage_types=applied_types, dice=dice, affected_states=affected_states)
            max_hp_before, max_hp_after = resolve_attack_max_hp_reduction(attack, actual_defender, damage_components)
            resolve_attack_ability_reduction(attack, actual_defender, dice, affected_states)
            applied_conditions = apply_hit_conditions(attack, actual_defender, attacker_event_id, round_number, affected_states, attacker, actual_event_id)
            hit_save = resolve_attack_save_rider(
                attacker, actual_defender, attack, dice, round_number=round_number,
                attacker_event_id=attacker_event_id, distance_ft=distance_ft,
                affected_states=affected_states, advantage_sources=saving_throw_advantage_sources,
            )
            applied_conditions.extend(item for item in hit_save.applied_effect_ids if item not in applied_conditions)
            topple = resolve_topple_hit(attacker, actual_defender, attack, dice)
            if topple.applied and "prone" not in applied_conditions: applied_conditions.append("prone")
            weapon_sap_applied = apply_weapon_sap(attacker, attacker_event_id, actual_defender, attack, round_number)
            if not weapon_sap_applied: tactical_sap_applied = apply_tactical_master_sap(attacker, attacker_event_id, actual_defender, attack, round_number)
            vex_applied = apply_vex_mastery(attacker, attacker_event_id, actual_event_id, attack, round_number, applied_total)
            end_rage_if_incapacitated(actual_defender)
        else:
            graze = resolve_graze_miss(attacker, actual_defender, attack, dice, affected_states)
            if graze is not None:
                damage_roll, damage_components, damage_outcome = graze
                end_rage_if_incapacitated(actual_defender)
            studied_applied = apply_studied_attack_miss(attacker, attacker_event_id, defender_event_id, round_number)
        description = build_attack_description(
            attacker, defender, actual_defender, attack, hit=hit, critical=critical, natural_1=natural_1,
            natural_1_ends_turn=natural_1_ends_turn, heroic_reroll=heroic_reroll,
            damage_total=damage_roll.total if damage_roll is not None else None, studied_applied=studied_applied,
            redirect_used=redirect_used, parry_used=parry_used, weapon_sap_applied=weapon_sap_applied,
            tactical_sap_applied=tactical_sap_applied, vex_applied=vex_applied, topple=topple,
            damage_outcome=damage_outcome, applied_conditions=applied_conditions,
        )
        if hit_save.save_ability is not None:
            total = hit_save.save_roll.total if hit_save.save_roll is not None else "automatic"
            result = "succeeds" if hit_save.save_succeeded else "fails"
            description += f" {actual_defender.template.name} {result} DC {hit_save.save_dc} {hit_save.save_ability.title()} save ({total})."
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack", actor_id=attacker_event_id, actor_name=attacker.template.name,
            target_id=actual_event_id, target_name=actual_defender.template.name, attack_name=weapon.name, target_ac=target_ac,
            attack_roll=attack_roll,
            saving_throw_roll=hit_save.save_roll if hit_save.save_ability is not None else (topple.save_roll if topple else None),
            save_ability=hit_save.save_ability if hit_save.save_ability is not None else ("constitution" if topple and topple.save_dc is not None else None),
            save_dc=hit_save.save_dc if hit_save.save_ability is not None else (topple.save_dc if topple else None),
            save_succeeded=hit_save.save_succeeded if hit_save.save_ability is not None else (topple.save_succeeded if topple else None),
            damage_roll=damage_roll, damage_components=damage_components, applied_condition_ids=applied_conditions,
            hit=hit, critical=critical, turn_terminated=natural_1_ends_turn,
            turn_termination_reason="iron-pit-natural-1-attack" if natural_1_ends_turn else None,
            hp_before=hp_before, hp_after=actual_defender.current_hp, max_hp_before=max_hp_before, max_hp_after=max_hp_after,
            temporary_hp_before=temporary_hp_before, temporary_hp_after=actual_defender.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=actual_defender.death_save_successes, death_save_failures=actual_defender.death_save_failures,
            is_stable=actual_defender.is_stable, is_dead=actual_defender.is_dead, weapon_id=weapon.id, projectile=weapon.projectile,
            feature_id=feature_id, resource_remaining=resource_remaining,
            concentration_ended_effect_id=concentration_before if concentration_before and actual_defender.concentration is None else None,
            animation=weapon.animation, description=description,
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
