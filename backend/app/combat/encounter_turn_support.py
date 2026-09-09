from __future__ import annotations

import logging

from app.combat.cleric_channel_support import resolve_channel_support
from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.pit_policy import save_distance, target_order
from app.combat.saving_throws import legal_save_action
from app.combat.barbarian import finalize_rage_turn
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=True):
    try:
        if allow_surge:
            surge_events, sequence = resolve_action_surge_attack(
                sequence, round_number, attacker, setup, dice, turn_key,
            )
            events.extend(surge_events)
        rage_event, sequence = finalize_rage_turn(
            sequence, round_number, attacker.state, attacker.combatant_id,
        )
        if rage_event is not None:
            events.append(rage_event)
        return events, sequence
    except Exception:
        logger.exception("Failed to finalize turn for %s.", attacker.combatant_id)
        raise


def resolve_support_actions(sequence, round_number, member, setup, dice, turn_key):
    try:
        events: list[BattleEvent] = []
        healing_choice = choose_healing_action(member, setup, turn_key)
        if healing_choice is not None and healing_choice[1].state.current_hp == 0:
            action, target = healing_choice
            events.append(resolve_healing(sequence, round_number, member, target, action, dice, turn_key))
            sequence += 1
        removal_choice = choose_condition_removal_action(member, setup, turn_key)
        if removal_choice is not None:
            action, target, conditions = removal_choice
            events.append(resolve_condition_removal(sequence, round_number, member, target, action, conditions, turn_key))
            sequence += 1
        healing_choice = choose_healing_action(member, setup, turn_key)
        if healing_choice is not None:
            action, target = healing_choice
            events.append(resolve_healing(sequence, round_number, member, target, action, dice, turn_key))
            sequence += 1
        channel_events, sequence = resolve_channel_support(sequence, round_number, member, setup, dice)
        events.extend(channel_events)
        return events, sequence
    except Exception:
        logger.exception("Failed support-action stage for %s.", member.combatant_id)
        raise


def save_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance):
                    return target, action, distance
        return None
    except Exception:
        logger.exception("Failed save-action choice for %s.", attacker.combatant_id)
        raise
