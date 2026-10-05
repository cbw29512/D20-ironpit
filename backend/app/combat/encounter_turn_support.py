from __future__ import annotations

import logging

from app.combat.resources import resource_available

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.barbarian import finalize_rage_turn
from app.combat.bonus_action_follow_up import resolve_bonus_action_follow_up
from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.condition_counter_policy import choose_condition_counter_spell
from app.combat.cleric_channel_support import resolve_channel_support
from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.effect_removal import choose_effect_removal_action, resolve_effect_removal
from app.combat.d20_bonus_dice import resolve_d20_bonus_die_grant
from app.combat.d20_bonus_die_support import choose_d20_bonus_die_action
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.frenzy_2014 import resolve_frenzy_bonus_attack
from app.combat.healing_support import resolve_healing_support
from app.combat.monk_bonus_attacks_2014 import resolve_monk_bonus_attacks
from app.combat.paladin_channel_divinity_2014 import resolve_paladin_channel_support
from app.combat.pit_policy import save_distance, target_order
from app.combat.spell_resolution import resolve_spell
from app.combat.encounter_turn_utility import resolve_control_support
from app.combat.saving_throws import legal_save_action
from app.combat.tactical_actions import resolve_defensive_tactical_grant
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
        bonus_attack_events, sequence = resolve_bonus_attack_grant(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(bonus_attack_events)
        if bonus_attack_events:
            follow_up = resolve_bonus_action_follow_up(
                sequence,
                round_number,
                attacker,
                bonus_attack_events[-1].feature_id,
                turn_key,
                dice,
            )
            if follow_up is not None:
                events.append(follow_up)
                sequence += 1
        defensive = resolve_defensive_tactical_grant(sequence, round_number, attacker, dice)
        if defensive is not None:
            events.append(defensive)
            sequence += 1
            follow_up = resolve_bonus_action_follow_up(
                sequence,
                round_number,
                attacker,
                defensive.feature_id,
                turn_key,
                dice,
            )
            if follow_up is not None:
                events.append(follow_up)
                sequence += 1
        monk_events, sequence = resolve_monk_bonus_attacks(
            sequence,
            round_number,
            attacker,
            setup,
            dice,
            turn_key,
            events,
        )
        events.extend(monk_events)
        frenzy_events, sequence = resolve_frenzy_bonus_attack(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(frenzy_events)
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
        bonus_before = member.state.bonus_action_available
        healing_events, sequence = resolve_healing_support(
            sequence, round_number, member, setup, dice, turn_key, downed_only=True,
        )
        events.extend(healing_events)
        if bonus_before and not member.state.bonus_action_available and healing_events:
            follow_up = resolve_bonus_action_follow_up(
                sequence, round_number, member, healing_events[-1].feature_id, turn_key, dice,
            )
            if follow_up is not None:
                events.append(follow_up)
                sequence += 1
        removal_choice = choose_condition_removal_action(member, setup, turn_key)
        if removal_choice is not None:
            action, target, conditions = removal_choice
            events.append(resolve_condition_removal(sequence, round_number, member, target, action, conditions, turn_key))
            sequence += 1
        bonus_before = member.state.bonus_action_available
        healing_events, sequence = resolve_healing_support(
            sequence, round_number, member, setup, dice, turn_key,
        )
        events.extend(healing_events)
        if bonus_before and not member.state.bonus_action_available and healing_events:
            follow_up = resolve_bonus_action_follow_up(
                sequence, round_number, member, healing_events[-1].feature_id, turn_key, dice,
            )
            if follow_up is not None:
                events.append(follow_up)
                sequence += 1
        counter = choose_condition_counter_spell(member, setup, turn_key)
        if counter is not None:
            countered, sequence = resolve_spell(
                sequence, round_number, member, setup, counter, turn_key, dice,
            )
            events.extend(countered)
            return events, sequence
        effect_choice = choose_effect_removal_action(member, setup, turn_key)
        if effect_choice is not None:
            action, effect = effect_choice
            events.append(resolve_effect_removal(
                sequence, round_number, member, setup, action, effect, dice, turn_key,
            ))
            sequence += 1
        channel_events, sequence = resolve_channel_support(sequence, round_number, member, setup, dice)
        events.extend(channel_events)
        paladin_events, sequence = resolve_paladin_channel_support(
            sequence, round_number, member, setup, dice,
        )
        events.extend(paladin_events)
        d20_bonus_choice = choose_d20_bonus_die_action(member, setup, round_number)
        if d20_bonus_choice is not None:
            action, target = d20_bonus_choice
            events.append(resolve_d20_bonus_die_grant(sequence, round_number, member, target, action))
            sequence += 1
        control_events, sequence = resolve_control_support(
            sequence, round_number, member, setup, dice, turn_key,
        )
        events.extend(control_events)
        return events, sequence
    except Exception:
        logger.exception("Failed support-action stage for %s.", member.combatant_id)
        raise


def save_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                if action.action_cost != "action":
                    continue
                if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                    continue
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance):
                    return target, action, distance
        return None
    except Exception:
        logger.exception("Failed save-action choice for %s.", attacker.combatant_id)
        raise


def resolve_area_save_turn(events, sequence, round_number, member, setup, dice, turn_key):
    try:
        choice = choose_area_save(member, setup, action_cost="action")
        if choice is None:
            return None
        action, placement = choice
        area_events, sequence = resolve_area_save(
            sequence, round_number, member, setup, action, placement, dice,
        )
        events.extend(area_events)
        return finish_turn(events, sequence, round_number, member, setup, dice, turn_key)
    except Exception:
        logger.exception("Failed area-save turn stage for %s.", member.combatant_id)
        raise
