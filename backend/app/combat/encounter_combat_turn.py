from __future__ import annotations

import logging
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.hp_threshold_turn import resolve_hp_threshold_turn
from app.combat.encounter_main_action import resolve_post_move_action
from app.combat.landing_offense_policy import melee_can_land_now
from app.combat.offensive_movement_policy import melee_can_be_enabled_this_turn
from app.combat.action_economy import is_available
from app.combat.charge import resolve_charge_closing
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.deferred_save_effect import cleanup_deferred_effects
from app.combat.encounter_turn_support import finish_turn, resolve_support_actions
from app.combat.ability_check_escape import resolve_escape_check, should_escape_check
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.ongoing_spell_control import build_forced_retreat_event, forced_retreat_active
from app.combat.offensive_movement_policy import move_to_enable_offense
from app.combat.orc import should_use_adrenaline_rush, use_adrenaline_rush
from app.combat.paladin_auras_2014 import sync_paladin_auras_2014
from app.combat.persistent_spell_attacks import resolve_persistent_spell_attack
from app.combat.replacement_form_policy import resolve_replacement_form_setup
from app.combat.pit_policy import target_order
from app.combat.start_turn import begin_turn_with_events
from app.combat.targeted_concentration_damage import resolve_targeted_concentration_damage
from app.combat.timed_effect_control import suppresses_voluntary_turn
from app.combat.feature_activation_phase import resolve_feature_activation_phase
from app.combat.formation_rows import sync_formation_rows
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
logger = logging.getLogger(__name__)

def resolve_combat_turn(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one Iron Pit turn through shared legality, movement, and fallback policy."""
    try:
        events: list[BattleEvent] = []
        cleanup_deferred_effects(setup)
        cleanup_grapples(setup)
        sync_paladin_auras_2014(setup)
        sync_friendly_save_auras(setup)
        start_events, sequence = begin_turn_with_events(
            sequence, round_number, attacker.combatant_id, attacker.state, dice, member=attacker,
        )
        events.extend(start_events)
        for member in sync_formation_rows(setup):
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=member.combatant_id, actor_name=member.state.template.name,
                feature_id="formation-step-up", animation="movement",
                description=f"{member.state.template.name} steps to the front row.",
            ))
            sequence += 1
        turn_key = f"{round_number}:{attacker.combatant_id}"
        if suppresses_voluntary_turn(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=False)
        if forced_retreat_active(attacker.state):
            events.append(build_forced_retreat_event(sequence, round_number, attacker.combatant_id, attacker.state))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=False)
        support_events, sequence = resolve_support_actions(sequence, round_number, attacker, setup, dice, turn_key)
        events.extend(support_events)
        if is_incapacitated(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        activation_events, sequence = resolve_feature_activation_phase(sequence, round_number, attacker, setup, dice, turn_key)
        events.extend(activation_events)
        if should_escape_grapple(attacker.state):
            events.append(resolve_escape_grapple(
                sequence, round_number, attacker.combatant_id, attacker.state, dice, encounter_actor=attacker, setup=setup,
            ))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if should_escape_check(attacker.state):
            events.append(resolve_escape_check(sequence, round_number, attacker, dice, setup=setup))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if should_use_adrenaline_rush(attacker.state):
            adrenaline_event = use_adrenaline_rush(sequence, round_number, attacker.state, attacker.combatant_id)
            if adrenaline_event is not None:
                events.append(adrenaline_event)
                sequence += 1
        # Spend the strongest legal signature Action before optional damage setup.
        threshold_event, sequence = resolve_hp_threshold_turn(sequence, round_number, attacker, setup, dice)
        if threshold_event is not None:
            events.extend(threshold_event if isinstance(threshold_event, list) else [threshold_event])
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        targeted_damage_event = resolve_targeted_concentration_damage(
            sequence, round_number, attacker, setup, turn_key,
        )
        if targeted_damage_event is not None:
            events.append(targeted_damage_event)
            sequence += 1
        persistent_spell_event = resolve_persistent_spell_attack(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        if persistent_spell_event is not None:
            events.append(persistent_spell_event)
            sequence += 1
        form_events, sequence = resolve_replacement_form_setup(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        events.extend(form_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if not melee_can_land_now(attacker, setup) and not melee_can_be_enabled_this_turn(
            attacker, setup, turn_key,
        ):
            spell_events, sequence = resolve_best_spell_offense(
                sequence, round_number, attacker, setup, turn_key, dice,
            )
            events.extend(spell_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        targets = target_order(attacker, setup)
        if not targets:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        charge_events, sequence, charged = resolve_charge_closing(
            sequence, round_number, attacker, targets[0], dice, setup,
        )
        events.extend(charge_events)
        if charged:
            sync_paladin_auras_2014(setup)
            sync_friendly_save_auras(setup)
        if charged or attacker.state.is_dead or attacker.state.is_unconscious:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        movement_events, sequence = move_to_enable_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(movement_events)
        sync_paladin_auras_2014(setup)
        sync_friendly_save_auras(setup)
        if attacker.state.is_dead or attacker.state.is_unconscious or is_incapacitated(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        return resolve_post_move_action(events, sequence, round_number, attacker, target, setup, dice, turn_key)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Combat-turn resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Combat turn could not be resolved.") from exc
