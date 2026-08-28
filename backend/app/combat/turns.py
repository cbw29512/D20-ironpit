from __future__ import annotations

import logging

from app.combat.bonus_actions import (
    use_nimble_escape_disengage,
    use_nimble_escape_hide,
)
from app.combat.dice import DiceProvider
from app.combat.movement import move_toward_target, take_dash
from app.combat.policy import (
    preferred_approach_distance,
    select_weapon_attack,
    should_use_nimble_escape_disengage,
    should_use_nimble_escape_hide,
)
from app.combat.reactions import retreat_with_opportunity_check
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, DuelMode, WeaponAttack

logger = logging.getLogger(__name__)


def prepare_skirmish_retreat(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    duel_mode: DuelMode = DuelMode.OPEN,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        if duel_mode is not DuelMode.OPEN:
            return events, sequence
        if not should_use_nimble_escape_disengage(attacker, battlefield.distance_ft):
            return events, sequence

        events.append(
            use_nimble_escape_disengage(sequence, round_number, attacker, battlefield)
        )
        sequence += 1
        retreat_events, sequence = retreat_with_opportunity_check(
            sequence, round_number, attacker, defender, battlefield, dice
        )
        events.extend(retreat_events)
        return events, sequence
    except Exception as exc:
        logger.exception("Skirmish retreat failed for %s.", attacker.template.name)
        raise RuntimeError("Skirmish retreat could not be completed.") from exc


def prepare_nimble_hide(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    duel_mode: DuelMode = DuelMode.OPEN,
) -> tuple[list[BattleEvent], int]:
    try:
        if duel_mode is not DuelMode.OPEN:
            return [], sequence
        if not should_use_nimble_escape_hide(attacker, battlefield):
            return [], sequence
        event = use_nimble_escape_hide(
            sequence, round_number, attacker, battlefield, dice
        )
        return [event], sequence + 1
    except Exception as exc:
        logger.exception("Nimble Hide preparation failed for %s.", attacker.template.name)
        raise RuntimeError("Nimble Hide preparation could not be completed.") from exc


def _close_simple_arena(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    battlefield: BattlefieldState,
) -> tuple[list[BattleEvent], int]:
    if battlefield.distance_ft <= 5:
        return [], sequence
    desired = max(5, battlefield.distance_ft - 10)
    movement = move_toward_target(
        sequence, round_number, attacker, battlefield, desired
    )
    if movement is None:
        return [], sequence
    return [movement], sequence + 1


def prepare_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    battlefield: BattlefieldState,
    duel_mode: DuelMode = DuelMode.OPEN,
) -> tuple[WeaponAttack | None, list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        if duel_mode is DuelMode.CLOSE:
            close_events, sequence = _close_simple_arena(
                sequence, round_number, attacker, battlefield
            )
            events.extend(close_events)

        attack = select_weapon_attack(attacker, battlefield.distance_ft, duel_mode)
        if attack is not None and attacker.action_available:
            return attack, events, sequence

        desired = preferred_approach_distance(attacker, duel_mode)
        movement = move_toward_target(
            sequence, round_number, attacker, battlefield, desired
        )
        if movement is not None:
            events.append(movement)
            sequence += 1

        attack = select_weapon_attack(attacker, battlefield.distance_ft, duel_mode)
        if attack is not None and attacker.action_available:
            return attack, events, sequence

        if attacker.action_available:
            events.append(take_dash(sequence, round_number, attacker, battlefield))
            sequence += 1
            movement = move_toward_target(
                sequence, round_number, attacker, battlefield, desired
            )
            if movement is not None:
                events.append(movement)
                sequence += 1

        return None, events, sequence
    except Exception as exc:
        logger.exception("Attack preparation failed for %s.", attacker.template.name)
        raise RuntimeError("Turn preparation could not be completed.") from exc
