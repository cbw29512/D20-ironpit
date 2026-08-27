from __future__ import annotations

import logging

from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import DiceProvider
from app.combat.fighter import use_action_surge, use_second_wind
from app.combat.policy import should_use_action_surge, should_use_second_wind
from app.combat.state import begin_turn
from app.combat.turns import prepare_attack
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)


def _perform_attack_action(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        attack, prep_events, sequence = prepare_attack(
            sequence, round_number, attacker, battlefield
        )
        events = list(prep_events)
        if attack is None:
            return events, sequence

        attack_events = resolve_attack_action(
            sequence,
            round_number,
            attacker,
            defender,
            attack,
            battlefield.distance_ft,
            dice,
        )
        events.extend(attack_events)
        return events, sequence + len(attack_events)
    except Exception as exc:
        logger.exception("Attack-action turn execution failed for %s.", attacker.template.name)
        raise RuntimeError("Attack action could not be executed.") from exc


def execute_turn(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    fighter_features: bool = False,
) -> tuple[list[BattleEvent], int]:
    try:
        begin_turn(attacker)
        events: list[BattleEvent] = []

        if fighter_features and should_use_second_wind(attacker):
            events.append(use_second_wind(sequence, round_number, attacker, dice))
            sequence += 1

        action_events, sequence = _perform_attack_action(
            sequence, round_number, attacker, defender, battlefield, dice
        )
        events.extend(action_events)

        if not fighter_features or not defender.is_alive or not should_use_action_surge(attacker):
            return events, sequence

        events.append(use_action_surge(sequence, round_number, attacker))
        sequence += 1
        surge_events, sequence = _perform_attack_action(
            sequence, round_number, attacker, defender, battlefield, dice
        )
        events.extend(surge_events)
        return events, sequence
    except Exception as exc:
        logger.exception("Turn execution failed for %s.", attacker.template.name)
        raise RuntimeError("Turn could not be executed.") from exc
