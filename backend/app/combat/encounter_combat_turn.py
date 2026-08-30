from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.arena_closing import MELEE_BRAWL_DISTANCE_FT, resolve_simple_closing
from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage, finalize_rage_turn
from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance, select_nearest_target
from app.combat.encounter_turns import prepare_encounter_attack
from app.combat.fighter import use_second_wind
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.orc import use_adrenaline_rush
from app.combat.policy import should_use_second_wind
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.spell_policy import choose_spell
from app.combat.spell_resolution import resolve_spell
from app.combat.state import begin_turn
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _close_after_action(sequence, round_number, attacker, setup, dice):
    target = select_nearest_target(attacker, setup)
    if target is None or combatant_distance(attacker, target) <= MELEE_BRAWL_DISTANCE_FT:
        return [], sequence
    events, sequence, _ = move_toward_with_reactions(
        sequence, round_number, attacker, target, setup, MELEE_BRAWL_DISTANCE_FT, dice,
    )
    return events, sequence


def _finish_turn(events, sequence, round_number, attacker):
    rage_event, sequence = finalize_rage_turn(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event)
    return events, sequence


def _resolve_support_actions(sequence, round_number, member, setup, dice, turn_key):
    """Rescue 0-HP allies first, then clear urgent removable debuffs, then consider ordinary healing."""
    events: list[BattleEvent] = []
    healing_choice = choose_healing_action(member, setup)
    if healing_choice is not None and healing_choice[1].state.current_hp == 0:
        action, target = healing_choice
        events.append(resolve_healing(sequence, round_number, member, target, action, dice))
        sequence += 1
    removal_choice = choose_condition_removal_action(member, setup, turn_key)
    if removal_choice is not None:
        action, target, conditions = removal_choice
        events.append(resolve_condition_removal(sequence, round_number, member, target, action, conditions, turn_key))
        sequence += 1
    healing_choice = choose_healing_action(member, setup)
    if healing_choice is not None:
        action, target = healing_choice
        events.append(resolve_healing(sequence, round_number, member, target, action, dice))
        sequence += 1
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
    support_events, sequence = _resolve_support_actions(sequence, round_number, attacker, setup, dice, turn_key)
    events.extend(support_events)
    rage_event = enter_rage(sequence, round_number, attacker.state, attacker.combatant_id)
    if rage_event is not None:
        events.append(rage_event); sequence += 1
    if should_use_second_wind(attacker.state):
        events.append(use_second_wind(sequence, round_number, attacker.state, dice, attacker.combatant_id)); sequence += 1
    if should_escape_grapple(attacker.state):
        events.append(resolve_escape_grapple(sequence, round_number, attacker.combatant_id, attacker.state, dice)); sequence += 1
        return _finish_turn(events, sequence, round_number, attacker)
    adrenaline_event = use_adrenaline_rush(sequence, round_number, attacker.state, attacker.combatant_id)
    if adrenaline_event is not None:
        events.append(adrenaline_event); sequence += 1

    spell_choice = choose_spell(attacker, setup, turn_key)
    if spell_choice is not None:
        spell_events, sequence = resolve_spell(sequence, round_number, attacker, setup, spell_choice, turn_key, dice)
        events.extend(spell_events)
        if not is_available(attacker.state, "action"):
            return _finish_turn(events, sequence, round_number, attacker)
    if not is_available(attacker.state, "action"):
        moved, sequence = _close_after_action(sequence, round_number, attacker, setup, dice)
        events.extend(moved)
        return _finish_turn(events, sequence, round_number, attacker)

    closing, sequence, handled = resolve_simple_closing(sequence, round_number, attacker, target, dice, setup)
    events.extend(closing)
    if attacker.state.is_dead or attacker.state.is_unconscious:
        return _finish_turn(events, sequence, round_number, attacker)
    distance = combatant_distance(attacker, target)
    save_action = next((a for a in attacker.state.template.saving_throw_actions if legal_save_action(a, target, distance)), None)
    if not handled and attacker.state.template.attack_action is not None:
        action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
        events.extend(action_events)
        moved, sequence = _close_after_action(sequence, round_number, attacker, setup, dice)
        events.extend(moved)
    elif not handled and save_action is not None and is_available(attacker.state, "action"):
        events.append(resolve_save_action(sequence, round_number, attacker, target, save_action, distance, dice)); sequence += 1
    elif not handled:
        attack, prep_events, sequence = prepare_encounter_attack(sequence, round_number, attacker, target)
        events.extend(prep_events)
        if attack is not None and is_available(attacker.state, "action"):
            pack = pack_tactics_active(attacker, target, setup)
            events.append(resolve_attack(
                sequence, round_number, attacker.state, target.state, attack,
                combatant_distance(attacker, target), dice,
                actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
                advantage_sources=1 if pack else 0, feature_id="pack-tactics" if pack else None,
                close_enemy_active=close_ranged_threat_exists(attacker, setup),
            )); sequence += 1
    return _finish_turn(events, sequence, round_number, attacker)
