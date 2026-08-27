from __future__ import annotations

import logging

from app.combat.movement import move_toward_target, take_dash
from app.combat.policy import preferred_approach_distance, select_attack_weapon
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, Weapon

logger = logging.getLogger(__name__)


def prepare_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    battlefield: BattlefieldState,
) -> tuple[Weapon | None, list[BattleEvent], int]:
    """Apply arena movement policy until a legal attack is available or the Action is spent."""
    try:
        events: list[BattleEvent] = []
        weapon = select_attack_weapon(attacker, battlefield.distance_ft)
        if weapon is not None and attacker.action_available:
            return weapon, events, sequence

        desired = preferred_approach_distance(attacker)
        movement = move_toward_target(
            sequence, round_number, attacker, battlefield, desired
        )
        if movement is not None:
            events.append(movement)
            sequence += 1

        weapon = select_attack_weapon(attacker, battlefield.distance_ft)
        if weapon is not None and attacker.action_available:
            return weapon, events, sequence

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
