from __future__ import annotations

import logging
from typing import Any

from app.combat.attack_effect_resolution import AttackEffectResolution
from app.combat.attack_event_support import (
    attack_damage_reduction_description, build_attack_description, primary_attack_save_fields,
)
from app.combat.reaction_roll_penalties import reaction_penalty_description
from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def build_resolved_attack_event(
    *,
    sequence: int, round_number: int, attacker: CombatantState, defender: CombatantState,
    actual_defender: CombatantState, attack: WeaponAttack, attacker_event_id: str,
    actual_event_id: str, target_ac: int, attack_roll: Any, hit: bool, critical: bool,
    natural_1: bool, natural_1_ends_turn: bool, automatic_hit: bool, heroic_reroll: bool,
    redirect_used: bool, parry_used: bool, d20_override_feature_id: str | None,
    d20_override_name: str | None, miss_override_feature_id: str | None,
    miss_override_name: str | None, outcome_adjustment_feature_id: str | None,
    outcome_adjustment_name: str | None, d20_bonus_source_name: str | None,
    reaction_penalty: Any, feature_id: str | None, effects: AttackEffectResolution,
    hp_before: int, temporary_hp_before: int, death_success_before: int,
    death_failure_before: int, concentration_before: str | None,
) -> BattleEvent:
    """Build the immutable audit event after generic attack mechanics are resolved."""
    try:
        weapon = attack.weapon
        description = build_attack_description(
            attacker_name=attacker.template.name, defender_name=defender.template.name,
            actual_defender_name=actual_defender.template.name, weapon_name=weapon.name,
            damage_type=weapon.damage_type.value, hit=hit, critical=critical,
            natural_1=natural_1, natural_1_ends_turn=natural_1_ends_turn,
            heroic_reroll=heroic_reroll, redirect_used=redirect_used, parry_used=parry_used,
            d20_override_feature_id=d20_override_feature_id, d20_override_name=d20_override_name,
            miss_override_feature_id=miss_override_feature_id, miss_override_name=miss_override_name,
            damage_roll=effects.damage_roll, studied_applied=effects.studied_applied,
            weapon_sap_applied=effects.weapon_sap_applied,
            tactical_sap_applied=effects.tactical_sap_applied, vex_applied=effects.vex_applied,
            save_damage=effects.save_damage, on_hit_save=effects.on_hit_save,
            on_hit_maximum_hp_save=effects.on_hit_maximum_hp_save,
            contested_movement=effects.contested_movement,
            cunning_strike_obscure=effects.cunning_strike_obscure,
            cunning_strike=effects.cunning_strike, topple=effects.topple,
            damage_outcome=effects.damage_outcome, applied_conditions=effects.applied_conditions,
            deferred_effect_armed=effects.deferred_effect_armed,
        )
        if automatic_hit:
            description += " The attack automatically hits its source-owned Grappled target."
        description += attack_damage_reduction_description(effects, actual_defender.template.name)
        if d20_bonus_source_name:
            description += f" {d20_bonus_source_name} adds its bonus die to the attack roll."
        if outcome_adjustment_name:
            description += f" {outcome_adjustment_name} adjusts the resolved D20 Test."
        if reaction_penalty is not None:
            description += reaction_penalty_description(reaction_penalty)
        if effects.exile_applied is not None:
            description += f" {actual_defender.template.name} is Banished until the source-relative return point."
        save_roll, save_ability, save_dc, save_succeeded = primary_attack_save_fields(
            effects.save_damage, effects.on_hit_save, effects.on_hit_maximum_hp_save,
            effects.contested_movement, effects.cunning_strike_obscure,
            effects.cunning_strike, effects.topple,
        )
        contested = effects.contested_movement
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker_event_id, actor_name=attacker.template.name,
            target_id=actual_event_id, target_name=actual_defender.template.name,
            attack_name=weapon.name, target_ac=target_ac, attack_roll=attack_roll,
            saving_throw_roll=save_roll, save_ability=save_ability, save_dc=save_dc,
            save_succeeded=save_succeeded, damage_roll=effects.damage_roll,
            damage_components=effects.damage_components,
            applied_condition_ids=effects.applied_conditions,
            ability_check_roll=contested.target_roll if contested else None,
            check_ability=contested.target_ability if contested else None,
            check_dc=contested.source_roll.total if contested and contested.source_roll else None,
            check_succeeded=contested.target_succeeded if contested else None,
            hit=hit, critical=critical,
            damage_reduction_zeroed_attack=effects.damage_reduction_zeroed_attack,
            turn_terminated=natural_1_ends_turn,
            turn_termination_reason="iron-pit-natural-1-attack" if natural_1_ends_turn else None,
            hp_before=hp_before, hp_after=actual_defender.current_hp,
            temporary_hp_before=temporary_hp_before,
            temporary_hp_after=actual_defender.temporary_hp,
            death_save_successes_before=death_success_before,
            death_save_failures_before=death_failure_before,
            death_save_successes=actual_defender.death_save_successes,
            death_save_failures=actual_defender.death_save_failures,
            is_stable=actual_defender.is_stable, is_dead=actual_defender.is_dead,
            attack_id=attack.id, weapon_id=weapon.id, projectile=weapon.projectile,
            feature_id=(
                d20_override_feature_id or miss_override_feature_id
                or outcome_adjustment_feature_id or feature_id
            ),
            concentration_ended_effect_id=(
                concentration_before
                if concentration_before and actual_defender.concentration is None else None
            ),
            resource_remaining=(
                effects.exile_applied[1] if effects.exile_applied is not None
                else effects.deferred_effect_armed.resource_remaining
                if effects.deferred_effect_armed is not None else None
            ),
            animation=weapon.animation,
            description=description + consume_survival_save_log(actual_defender)
            + consume_zero_hp_replacement_log(actual_defender),
        )
    except Exception as exc:
        logger.exception(
            "Failed to build attack event for %s -> %s.",
            attacker.template.name, defender.template.name,
        )
        raise RuntimeError("Attack event could not be built.") from exc
