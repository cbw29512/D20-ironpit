from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log
import logging
from app.combat.action_economy import is_available, spend
from app.combat.attack_roll_resolution import resolve_attack_roll
from app.combat.attack_d20_outcome import resolve_attack_d20_outcome
from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.attack_event_support import build_attack_description, primary_attack_save_fields
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.modifier_stack import effective_armor_class
from app.combat.state import terminate_turn
from app.domain.models import BattleEvent, CombatantState, WeaponAttack
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
) -> BattleEvent:
    try:
        if spend_action and not is_available(attacker, "action"):
            raise ValueError("Action is not available for an attack.")
        weapon = attack.weapon; defender_event_id = target_event_id or defender.template.id
        attacker_event_id = actor_event_id or attacker.template.id
        roll_resolution = resolve_attack_roll(
            attacker,
            defender,
            attack,
            distance_ft,
            dice,
            defender_event_id=defender_event_id,
            round_number=round_number,
            turn_key=turn_key,
            advantage_sources=advantage_sources,
            other_disadvantage_sources=other_disadvantage_sources,
            close_enemy_active=close_enemy_active,
        )
        attack_roll = roll_resolution.roll
        mode = roll_resolution.mode
        heroic_reroll = roll_resolution.heroic_reroll
        brutal_strike_disadvantage = roll_resolution.brutal_strike_disadvantage
        if spend_action: spend(attacker, "action")
        actual_defender, actual_event_id, redirect_used = defender, defender_event_id, False
        if redirect_target is not None and redirect_target is not defender and defender.template.redirect_attack_reaction is not None and is_available(defender, "reaction"):
            spend(defender, "reaction"); actual_defender = redirect_target
            actual_event_id = redirect_target_event_id or redirect_target.template.id; redirect_used = True
        d20_outcome = resolve_attack_d20_outcome(
            attacker, actual_defender, attack, attack_roll, effective_armor_class(actual_defender),
        )
        attack_roll, target_ac, hit = d20_outcome.roll, d20_outcome.target_ac, d20_outcome.hit
        natural, parry_used = d20_outcome.natural, d20_outcome.parry_used
        d20_override_feature_id, d20_override_name = d20_outcome.d20_override_feature_id, d20_outcome.d20_override_source_name
        miss_override_feature_id, miss_override_name = d20_outcome.miss_override_feature_id, d20_outcome.miss_override_source_name
        natural_1 = natural == 1
        expanded_critical = natural >= attacker.template.progression_features.critical_hit_minimum
        natural_1_ends_turn = natural_1 and not off_turn and not (
            d20_override_feature_id or miss_override_feature_id
        )
        if natural_1_ends_turn:
            terminate_turn(attacker, "iron-pit-natural-1-attack")
        critical = bool(hit and miss_override_feature_id is None and (
            expanded_critical or (close_hit_is_automatic_critical(actual_defender) and distance_ft <= 5)
        ))
        hp_before = actual_defender.current_hp; temporary_hp_before = actual_defender.temporary_hp
        death_success_before = actual_defender.death_save_successes; death_failure_before = actual_defender.death_save_failures
        concentration_before = actual_defender.concentration.effect_id if actual_defender.concentration else None
        effects = resolve_attack_effects(
            attacker,
            actual_defender,
            attack,
            dice,
            hit=hit,
            critical=critical,
            mode=mode,
            round_number=round_number,
            attacker_event_id=attacker_event_id,
            defender_event_id=defender_event_id,
            actual_event_id=actual_event_id,
            turn_key=turn_key,
            bonus_damage=bonus_damage,
            affected_states=affected_states,
            sneak_attack_ally_available=sneak_attack_ally_available,
            brutal_strike_disadvantage=brutal_strike_disadvantage,
        )
        damage_roll, damage_components, damage_outcome = effects.damage_roll, effects.damage_components, effects.damage_outcome
        applied_conditions, save_damage, on_hit_save = effects.applied_conditions, effects.save_damage, effects.on_hit_save
        cunning_strike, cunning_strike_obscure, topple = effects.cunning_strike, effects.cunning_strike_obscure, effects.topple
        weapon_sap_applied, tactical_sap_applied = effects.weapon_sap_applied, effects.tactical_sap_applied
        vex_applied, studied_applied = effects.vex_applied, effects.studied_applied
        deferred_effect_armed = effects.deferred_effect_armed
        description = build_attack_description(
            attacker_name=attacker.template.name,
            defender_name=defender.template.name,
            actual_defender_name=actual_defender.template.name,
            weapon_name=weapon.name,
            damage_type=weapon.damage_type.value,
            hit=hit,
            critical=critical,
            natural_1=natural_1,
            natural_1_ends_turn=natural_1_ends_turn,
            heroic_reroll=heroic_reroll,
            redirect_used=redirect_used,
            parry_used=parry_used,
            d20_override_feature_id=d20_override_feature_id,
            d20_override_name=d20_override_name,
            miss_override_feature_id=miss_override_feature_id,
            miss_override_name=miss_override_name,
            damage_roll=damage_roll,
            studied_applied=studied_applied,
            weapon_sap_applied=weapon_sap_applied,
            tactical_sap_applied=tactical_sap_applied,
            vex_applied=vex_applied,
            save_damage=save_damage,
            on_hit_save=on_hit_save,
            cunning_strike_obscure=cunning_strike_obscure,
            cunning_strike=cunning_strike,
            topple=topple,
            damage_outcome=damage_outcome,
            applied_conditions=applied_conditions,
            deferred_effect_armed=deferred_effect_armed,
        )
        save_roll, save_ability, save_dc, save_succeeded = primary_attack_save_fields(
            save_damage, on_hit_save, cunning_strike_obscure, cunning_strike, topple,
        )
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack", actor_id=attacker_event_id, actor_name=attacker.template.name,
            target_id=actual_event_id, target_name=actual_defender.template.name, attack_name=weapon.name, target_ac=target_ac,
            attack_roll=attack_roll, saving_throw_roll=save_roll, save_ability=save_ability, save_dc=save_dc, save_succeeded=save_succeeded,
            damage_roll=damage_roll, damage_components=damage_components, applied_condition_ids=applied_conditions,
            hit=hit, critical=critical, turn_terminated=natural_1_ends_turn,
            turn_termination_reason="iron-pit-natural-1-attack" if natural_1_ends_turn else None,
            hp_before=hp_before, hp_after=actual_defender.current_hp,
            temporary_hp_before=temporary_hp_before, temporary_hp_after=actual_defender.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=actual_defender.death_save_successes, death_save_failures=actual_defender.death_save_failures,
            is_stable=actual_defender.is_stable, is_dead=actual_defender.is_dead, weapon_id=weapon.id, projectile=weapon.projectile,
            feature_id=d20_override_feature_id or miss_override_feature_id or feature_id, concentration_ended_effect_id=concentration_before if concentration_before and actual_defender.concentration is None else None,
            resource_remaining=(deferred_effect_armed.resource_remaining if deferred_effect_armed is not None else None),
            animation=weapon.animation, description=description + consume_survival_save_log(actual_defender) + consume_zero_hp_replacement_log(actual_defender),
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
