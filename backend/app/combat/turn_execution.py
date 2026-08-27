from __future__ import annotations

import logging

from app.combat.action_policy import select_standalone_save_action
from app.combat.attack_actions import resolve_attack_action
from app.combat.condition_timing import expire_turn_conditions
from app.combat.dice import DiceProvider
from app.combat.fighter import use_action_surge, use_second_wind
from app.combat.multiattack import resolve_multiattack_action
from app.combat.object_attack_actions import (
    resolve_object_priority_attack_action,
    select_linked_object,
)
from app.combat.policy import should_use_action_surge, should_use_second_wind
from app.combat.recharge import roll_recharges
from app.combat.save_actions import resolve_save_action
from app.combat.state import begin_turn
from app.combat.turns import prepare_attack, prepare_position
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)


def _perform_offensive_action(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    visible_source_ids: set[str],
) -> tuple[list[BattleEvent], int]:
    try:
        prep_events, sequence = prepare_position(
            sequence, round_number, attacker, defender, battlefield
        )
        events = list(prep_events)

        if select_linked_object(attacker, battlefield) is not None and attacker.action_available:
            action_events = resolve_object_priority_attack_action(
                sequence,
                round_number,
                attacker,
                defender,
                battlefield,
                dice,
                visible_source_ids,
            )
            events.extend(action_events)
            return events, sequence + len(action_events)

        save_action = select_standalone_save_action(
            attacker, defender, battlefield.distance_ft
        )
        if save_action is not None:
            action_events = resolve_save_action(
                sequence,
                round_number,
                attacker,
                defender,
                battlefield.distance_ft,
                save_action,
                dice,
                battlefield=battlefield,
            )
            events.extend(action_events)
            return events, sequence + len(action_events)

        attack, attack_prep_events, sequence = prepare_attack(
            sequence, round_number, attacker, defender, battlefield
        )
        events.extend(attack_prep_events)
        if attack is None:
            return events, sequence

        resolver = (
            resolve_multiattack_action
            if attacker.template.multiattack is not None
            else resolve_attack_action
        )
        action_events = resolver(
            sequence,
            round_number,
            attacker,
            defender,
            battlefield,
            dice,
            visible_source_ids,
        )
        events.extend(action_events)
        return events, sequence + len(action_events)
    except Exception as exc:
        logger.exception("Offensive turn execution failed for %s.", attacker.template.name)
        raise RuntimeError("Offensive action could not be executed.") from exc


def execute_turn(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    fighter_features: bool = False,
    combatants: list[CombatantState] | None = None,
    visible_source_ids: set[str] | None = None,
) -> tuple[list[BattleEvent], int]:
    try:
        roster = combatants or [attacker, defender]
        visible_sources = visible_source_ids or {defender.instance_id}
        events = expire_turn_conditions(sequence, round_number, attacker, roster, "start")
        sequence += len(events)
        recharge_events = roll_recharges(sequence, round_number, attacker, dice)
        events.extend(recharge_events)
        sequence += len(recharge_events)
        begin_turn(attacker)

        if fighter_features and should_use_second_wind(attacker):
            events.append(use_second_wind(sequence, round_number, attacker, dice))
            sequence += 1

        action_events, sequence = _perform_offensive_action(
            sequence, round_number, attacker, defender, battlefield, dice, visible_sources
        )
        events.extend(action_events)

        if fighter_features and defender.is_alive and should_use_action_surge(attacker):
            events.append(use_action_surge(sequence, round_number, attacker))
            sequence += 1
            surge_events, sequence = _perform_offensive_action(
                sequence, round_number, attacker, defender, battlefield, dice, visible_sources
            )
            events.extend(surge_events)

        end_events = expire_turn_conditions(sequence, round_number, attacker, roster, "end")
        events.extend(end_events)
        return events, sequence + len(end_events)
    except Exception as exc:
        logger.exception("Turn execution failed for %s.", attacker.template.name)
        raise RuntimeError("Turn could not be executed.") from exc
