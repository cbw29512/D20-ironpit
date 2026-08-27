from __future__ import annotations

import logging

from app.combat.conditions import can_willingly_approach
from app.combat.movement import move_toward_target, take_dash
from app.combat.policy import preferred_approach_distance, select_weapon_attack
from app.combat.prone import stand_from_prone
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def prepare_position(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
) -> tuple[list[BattleEvent], int]:
    """Stand if needed, then spend normal movement closing toward the preferred melee distance."""
    try:
        events: list[BattleEvent] = []
        standing = stand_from_prone(sequence, round_number, attacker)
        if standing is not None:
            events.append(standing)
            sequence += 1

        desired = preferred_approach_distance(attacker)
        if battlefield.distance_ft <= desired:
            return events, sequence
        if not can_willingly_approach(attacker, defender.instance_id):
            return events, sequence

        movement = move_toward_target(
            sequence, round_number, attacker, defender.instance_id, battlefield, desired
        )
        if movement is not None:
            events.append(movement)
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Position preparation failed for %s.", attacker.template.name)
        raise RuntimeError("Turn positioning could not be completed.") from exc


def prepare_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
) -> tuple[WeaponAttack | None, list[BattleEvent], int]:
    """Close first, attack if legal, otherwise Dash toward melee without kiting."""
    try:
        events, sequence = prepare_position(
            sequence, round_number, attacker, defender, battlefield
        )
        attack = select_weapon_attack(attacker, battlefield.distance_ft)
        if attack is not None and attacker.action_available:
            return attack, events, sequence

        desired = preferred_approach_distance(attacker)
        if not can_willingly_approach(attacker, defender.instance_id):
            return None, events, sequence

        if attacker.action_available:
            events.append(take_dash(sequence, round_number, attacker, battlefield))
            sequence += 1
            movement = move_toward_target(
                sequence, round_number, attacker, defender.instance_id, battlefield, desired
            )
            if movement is not None:
                events.append(movement)
                sequence += 1

        return None, events, sequence
    except Exception as exc:
        logger.exception("Attack preparation failed for %s.", attacker.template.name)
        raise RuntimeError("Turn preparation could not be completed.") from exc
