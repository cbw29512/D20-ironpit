from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.arena_closing import MELEE_BRAWL_DISTANCE_FT, resolve_simple_closing
from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage, finalize_rage_turn
from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.encounter_turns import prepare_encounter_attack
from app.combat.fighter import use_second_wind
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.orc import use_adrenaline_rush
from app.combat.policy import should_use_second_wind
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.state import begin_turn
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _close_after_action(sequence, round_number, attacker, setup):
    target = select_nearest_target(attacker, setup)
    if target is None or combatant_distance(attacker, target) <= MELEE_BRAWL_DISTANCE_FT:
        return [], sequence
    movement = move_toward_combatant(sequence, round_number, attacker, target, MELEE_BRAWL_DISTANCE_FT)
    return ([], sequence) if movement is None else ([movement], sequence + 1)


def _finish_turn(events, sequence, round_number, attacker):
    rage_event, sequence = finalize_rage_turn(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event)
    return events, sequence


def resolve_combat_turn(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one living combatant turn through the canonical Iron Pit rules."""
    events: list[BattleEvent] = []
    cleanup_grapples(setup)
    begin_turn(attacker.state)
    healing_choice = choose_healing_action(attacker, setup)
    if healing_choice is not None:
        healing_action, healing_target = healing_choice
        events.append(resolve_healing(sequence, round_number, attacker, healing_target, healing_action, dice))
        sequence += 1
    rage_event = enter_rage(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event)
        sequence += 1
    if should_use_second_wind(attacker.state):
        events.append(use_second_wind(sequence, round_number, attacker.state, dice, attacker.combatant_id))
        sequence += 1
    if should_escape_grapple(attacker.state):
        events.append(resolve_escape_grapple(sequence, round_number, attacker.combatant_id, attacker.state, dice))
        sequence += 1
        return _finish_turn(events, sequence, round_number, attacker)
    adrenaline_event = use_adrenaline_rush(sequence, round_number, attacker.state, attacker.combatant_id)
    if adrenaline_event is not None:
        events.append(adrenaline_event)
        sequence += 1
    if not is_available(attacker.state, "action"):
        movement_events, sequence = _close_after_action(sequence, round_number, attacker, setup)
        events.extend(movement_events)
        return _finish_turn(events, sequence, round_number, attacker)
    closing_events, sequence, closing_handled = resolve_simple_closing(sequence, round_number, attacker, target, dice)
    events.extend(closing_events)
    distance = combatant_distance(attacker, target)
    save_action = next((a for a in attacker.state.template.saving_throw_actions if legal_save_action(a, target, distance)), None)
    if not closing_handled and attacker.state.template.attack_action is not None:
        action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
        events.extend(action_events)
        movement_events, sequence = _close_after_action(sequence, round_number, attacker, setup)
        events.extend(movement_events)
    elif not closing_handled and save_action is not None and is_available(attacker.state, "action"):
        events.append(resolve_save_action(sequence, round_number, attacker, target, save_action, distance, dice))
        sequence += 1
    elif not closing_handled:
        attack, prep_events, sequence = prepare_encounter_attack(sequence, round_number, attacker, target)
        events.extend(prep_events)
        if attack is not None and is_available(attacker.state, "action"):
            pack = pack_tactics_active(attacker, target, setup)
            events.append(resolve_attack(
                sequence, round_number, attacker.state, target.state, attack,
                combatant_distance(attacker, target), dice,
                actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
                advantage_sources=1 if pack else 0, feature_id="pack-tactics" if pack else None,
            ))
            sequence += 1
    return _finish_turn(events, sequence, round_number, attacker)
