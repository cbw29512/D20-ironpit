from __future__ import annotations

import logging

from app.combat.attack_actions import resolve_attack_action
from app.combat.condition_timing import expire_turn_conditions
from app.combat.dice import DiceProvider
from app.combat.fighter import use_action_surge, use_second_wind
from app.combat.multiattack import resolve_multiattack_action
from app.combat.policy import should_use_action_surge, should_use_second_wind
from app.combat.state import begin_turn
from app.combat.turns import prepare_attack
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
        attack, prep_events, sequence = prepare_attack(
            sequence, round_number, attacker, defender, battlefield
        )
        events = list(prep_events)
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
