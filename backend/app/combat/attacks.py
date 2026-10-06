from __future__ import annotations

import logging
from app.combat.action_economy import is_available, spend
from app.combat.timed_attack_cap import register_turn_attack
from app.combat.attack_roll_resolution import resolve_attack_roll
from app.combat.attack_legality import attack_allowed_against, attack_is_automatic_hit
from app.combat.attack_d20_outcome import resolve_attack_d20_outcome
from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.attack_event_builder import build_resolved_attack_event
from app.combat.brutal_strike import clear_brutal_strike_pending
from app.combat.condition_rules import close_hit_is_automatic_critical
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.modifier_stack import effective_armor_class
from app.combat.reaction_roll_penalties import apply_reaction_roll_penalty_if_useful
from app.combat.state import terminate_turn
from app.domain.models import BattleEvent, CombatantState, RollMode, WeaponAttack
from app.domain.encounters import EncounterCombatant, EncounterSetup
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
    reaction_setup: EncounterSetup | None = None,
    reaction_roller: EncounterCombatant | None = None,
) -> BattleEvent:
    try:
        register_turn_attack(attacker, off_turn=off_turn)
        if spend_action and not is_available(attacker, "action"):
            raise ValueError("Action is not available for an attack.")
        defender_event_id = target_event_id or defender.template.id
        attacker_event_id = actor_event_id or attacker.template.id
        if not attack_allowed_against(attack, attacker_event_id, defender, affected_states):
            raise ValueError(f"{attack.id} cannot target {defender_event_id} under its current target policy.")
        automatic_hit = attack_is_automatic_hit(attack, attacker_event_id, defender)
        attack_roll = None
        mode = RollMode.NORMAL
        heroic_reroll = False
        brutal_strike_disadvantage = 0
        d20_bonus_source_name = None
        reaction_penalty = None
        actual_defender, actual_event_id, redirect_used = defender, defender_event_id, False
        parry_used = False
        d20_override_feature_id = d20_override_name = None
        miss_override_feature_id = miss_override_name = None
        outcome_adjustment_feature_id = outcome_adjustment_name = None
        natural = 0
        target_ac = effective_armor_class(defender)
        hit = automatic_hit

        if not automatic_hit:
            roll_resolution = resolve_attack_roll(
                attacker,
                defender,
                attack,
                distance_ft,
                dice,
                defender_event_id=defender_event_id,
                attacker_event_id=attacker_event_id,
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
            d20_bonus_source_name = roll_resolution.d20_bonus_source_name
            if reaction_setup is not None and reaction_roller is not None:
                reaction_penalty = apply_reaction_roll_penalty_if_useful(
                    reaction_roller,
                    reaction_setup,
                    "attack",
                    attack_roll,
                    dice,
                    threshold=effective_armor_class(defender),
                )
                if reaction_penalty is not None:
                    attack_roll = reaction_penalty.roll

        if spend_action:
            spend(attacker, "action")

        if not automatic_hit:
            if (
                redirect_target is not None
                and redirect_target is not defender
                and defender.template.redirect_attack_reaction is not None
                and is_available(defender, "reaction")
            ):
                spend(defender, "reaction")
                actual_defender = redirect_target
                actual_event_id = redirect_target_event_id or redirect_target.template.id
                redirect_used = True
            assert attack_roll is not None
            d20_outcome = resolve_attack_d20_outcome(
                attacker,
                actual_defender,
                attack,
                attack_roll,
                effective_armor_class(actual_defender),
                encounter_roller=reaction_roller,
                setup=reaction_setup,
                dice=dice,
            )
            attack_roll, target_ac, hit = d20_outcome.roll, d20_outcome.target_ac, d20_outcome.hit
            natural, parry_used = d20_outcome.natural, d20_outcome.parry_used
            d20_override_feature_id, d20_override_name = (
                d20_outcome.d20_override_feature_id,
                d20_outcome.d20_override_source_name,
            )
            miss_override_feature_id, miss_override_name = (
                d20_outcome.miss_override_feature_id,
                d20_outcome.miss_override_source_name,
            )
            outcome_adjustment_feature_id = d20_outcome.outcome_adjustment_feature_id
            outcome_adjustment_name = d20_outcome.outcome_adjustment_source_name

        if not hit:
            clear_brutal_strike_pending(attacker, turn_key)
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
            natural_roll=natural,
            setup=reaction_setup,
        )
        return build_resolved_attack_event(
            sequence=sequence, round_number=round_number, attacker=attacker, defender=defender,
            actual_defender=actual_defender, attack=attack, attacker_event_id=attacker_event_id,
            actual_event_id=actual_event_id, target_ac=target_ac, attack_roll=attack_roll,
            hit=hit, critical=critical, natural_1=natural_1,
            natural_1_ends_turn=natural_1_ends_turn, automatic_hit=automatic_hit,
            heroic_reroll=heroic_reroll, redirect_used=redirect_used, parry_used=parry_used,
            d20_override_feature_id=d20_override_feature_id, d20_override_name=d20_override_name,
            miss_override_feature_id=miss_override_feature_id, miss_override_name=miss_override_name,
            outcome_adjustment_feature_id=outcome_adjustment_feature_id,
            outcome_adjustment_name=outcome_adjustment_name,
            d20_bonus_source_name=d20_bonus_source_name, reaction_penalty=reaction_penalty,
            feature_id=feature_id, effects=effects, hp_before=hp_before,
            temporary_hp_before=temporary_hp_before, death_success_before=death_success_before,
            death_failure_before=death_failure_before, concentration_before=concentration_before,
        )
    except Exception as exc:
        logger.exception("Attack failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack resolution failed.") from exc
