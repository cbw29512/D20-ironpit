from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.arena_closing import MELEE_BRAWL_DISTANCE_FT, resolve_simple_closing
from app.combat.attack_actions import resolve_attack_action
from app.combat.barbarian import enter_rage, finalize_rage_turn
from app.combat.cleric_channel_support import resolve_channel_support
from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.encounter_turns import prepare_encounter_attack
from app.combat.fighter import use_second_wind
from app.combat.formation import backline_holds_position
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.ongoing_spell_control import build_forced_retreat_event, forced_retreat_active
from app.combat.opening_burst import opening_feature_id
from app.combat.orc import should_use_adrenaline_rush, use_adrenaline_rush
from app.combat.policy import should_use_second_wind
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.state import begin_turn
from app.combat.tactical_shift import resolve_tactical_shift
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
def _close_after_action(sequence, round_number, attacker, setup, dice, turn_key):
    if is_incapacitated(attacker.state) or backline_holds_position(attacker, setup):
        return [], sequence
    target = select_nearest_target(attacker, setup)
    if target is None or combatant_distance(attacker, target) <= MELEE_BRAWL_DISTANCE_FT:
        return [], sequence
    events, sequence, _ = move_toward_with_reactions(
        sequence, round_number, attacker, target, setup, MELEE_BRAWL_DISTANCE_FT, dice,
        turn_key=turn_key,
    )
    return events, sequence


def _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=True):
    if allow_surge:
        surge_events, sequence = resolve_action_surge_attack(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(surge_events)
    rage_event, sequence = finalize_rage_turn(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event)
    return events, sequence
def _resolve_support_actions(sequence, round_number, member, setup, dice, turn_key):
    """Rescue 0-HP allies first, then clear urgent removable debuffs, then consider ordinary healing."""
    events: list[BattleEvent] = []
    healing_choice = choose_healing_action(member, setup, turn_key)
    if healing_choice is not None and healing_choice[1].state.current_hp == 0:
        action, target = healing_choice
        events.append(resolve_healing(sequence, round_number, member, target, action, dice, turn_key)); sequence += 1
    removal_choice = choose_condition_removal_action(member, setup, turn_key)
    if removal_choice is not None:
        action, target, conditions = removal_choice
        events.append(resolve_condition_removal(sequence, round_number, member, target, action, conditions, turn_key)); sequence += 1
    healing_choice = choose_healing_action(member, setup, turn_key)
    if healing_choice is not None:
        action, target = healing_choice
        events.append(resolve_healing(sequence, round_number, member, target, action, dice, turn_key)); sequence += 1
    channel_events, sequence = resolve_channel_support(sequence, round_number, member, setup, dice); events.extend(channel_events)
    return events, sequence


def resolve_combat_turn(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one living combatant turn through the canonical Iron Pit rules."""
    events: list[BattleEvent] = []
    cleanup_grapples(setup)
    begin_turn(attacker.state)
    turn_key = f"{round_number}:{attacker.combatant_id}"
    if forced_retreat_active(attacker.state):
        events.append(build_forced_retreat_event(sequence, round_number, attacker.combatant_id, attacker.state)); sequence += 1
        return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=False)
    support_events, sequence = _resolve_support_actions(sequence, round_number, attacker, setup, dice, turn_key)
    events.extend(support_events)
    if is_incapacitated(attacker.state):
        return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
    rage_event = enter_rage(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event); sequence += 1
    if should_use_second_wind(attacker.state):
        events.append(use_second_wind(sequence, round_number, attacker.state, dice, attacker.combatant_id)); sequence += 1
        shift_event = resolve_tactical_shift(sequence, round_number, attacker, setup)
        if shift_event is not None:
            events.append(shift_event); sequence += 1
    if should_escape_grapple(attacker.state):
        events.append(resolve_escape_grapple(sequence, round_number, attacker.combatant_id, attacker.state, dice)); sequence += 1
        return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
    if should_use_adrenaline_rush(attacker.state):
        adrenaline_event = use_adrenaline_rush(sequence, round_number, attacker.state, attacker.combatant_id)
        if adrenaline_event is not None:
            events.append(adrenaline_event); sequence += 1
    spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
    events.extend(spell_events)
    if not is_available(attacker.state, "action"):
        return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

    closing, sequence, handled = resolve_simple_closing(sequence, round_number, attacker, target, dice, setup, turn_key)
    events.extend(closing)
    if attacker.state.is_dead or attacker.state.is_unconscious:
        return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
    distance = combatant_distance(attacker, target)
    save_action = next((a for a in attacker.state.template.saving_throw_actions if legal_save_action(a, target, distance)), None)
    if not handled and attacker.state.template.attack_action is not None:
        action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
        events.extend(action_events)
        moved, sequence = _close_after_action(sequence, round_number, attacker, setup, dice, turn_key); events.extend(moved)
    elif not handled and save_action is not None and is_available(attacker.state, "action"):
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        events.append(resolve_save_action(
            sequence, round_number, attacker, target, save_action, distance, dice, affected_states=affected,
        )); sequence += 1
    elif not handled:
        attack, prep_events, sequence = prepare_encounter_attack(sequence, round_number, attacker, target)
        events.extend(prep_events)
        if attack is not None and is_available(attacker.state, "action"):
            pack = pack_tactics_active(attacker, target, setup)
            feature = opening_feature_id(round_number, attacker, setup) or ("pack-tactics" if pack else None)
            events.append(resolve_encounter_attack(
                sequence, round_number, attacker, target, attack, combatant_distance(attacker, target), dice, setup,
                advantage_sources=1 if pack else 0, feature_id=feature, turn_key=turn_key, allow_reckless=True,
            )); sequence += 1
    return _finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
