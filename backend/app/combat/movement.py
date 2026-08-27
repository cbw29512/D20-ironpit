from __future__ import annotations

import logging

from app.combat.conditions import can_willingly_approach
from app.combat.dice import DiceProvider
from app.combat.movement_state import add_movement_allowance, current_speed_ft, spend_movement
from app.combat.reactions import resolve_opportunity_attack
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)


def move_toward_target(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    target_id: str,
    battlefield: BattlefieldState,
    desired_distance_ft: int,
) -> BattleEvent | None:
    """Spend movement to close distance while enforcing willingness restrictions."""
    try:
        if desired_distance_ft < 0:
            raise ValueError("Desired distance cannot be negative.")
        needed = max(0, battlefield.distance_ft - desired_distance_ft)
        if needed > 0 and not can_willingly_approach(mover, target_id):
            raise ValueError("Frightened creature cannot willingly approach its fear source.")
        moved = min(needed, mover.movement_remaining_ft)
        if moved <= 0:
            return None

        before = battlefield.distance_ft
        battlefield.distance_ft -= moved
        spend_movement(mover, moved)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="movement",
            actor_id=mover.instance_id,
            actor_name=mover.template.name,
            target_id=target_id,
            distance_before_ft=before,
            distance_after_ft=battlefield.distance_ft,
            movement_ft=moved,
            animation="advance",
            description=f"{mover.template.name} advances {moved} feet.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Movement resolution failed for %s.", mover.template.name)
        raise RuntimeError("Movement could not be resolved.") from exc


def move_away_from_target(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    reactor: CombatantState,
    battlefield: BattlefieldState,
    requested_ft: int,
    dice: DiceProvider,
    *,
    mover_visible: bool = True,
) -> list[BattleEvent]:
    """Spend voluntary movement away, resolving any OA before the departure completes."""
    try:
        moved = min(max(0, requested_ft), mover.movement_remaining_ft)
        if moved <= 0:
            return []

        before = battlefield.distance_ft
        after = before + moved
        events: list[BattleEvent] = []
        reaction = resolve_opportunity_attack(
            sequence,
            round_number,
            reactor,
            mover,
            before,
            after,
            dice,
            mover_visible=mover_visible,
        )
        if reaction is not None:
            events.append(reaction)
            sequence += 1
            if not mover.is_alive:
                return events

        battlefield.distance_ft = after
        spend_movement(mover, moved)
        events.append(BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="movement",
            actor_id=mover.instance_id,
            actor_name=mover.template.name,
            target_id=reactor.instance_id,
            target_name=reactor.template.name,
            distance_before_ft=before,
            distance_after_ft=after,
            movement_ft=moved,
            animation="retreat",
            description=f"{mover.template.name} moves {moved} feet away.",
        ))
        return events
    except Exception as exc:
        logger.exception("Departure movement failed for %s.", mover.template.name)
        raise RuntimeError("Departure movement could not be resolved.") from exc


def take_dash(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    battlefield: BattlefieldState,
) -> BattleEvent:
    """Spend the Action to gain extra movement equal to the creature's current Speed."""
    try:
        if not mover.action_available:
            raise ValueError("Action is not available for Dash.")
        mover.action_available = False
        bonus = current_speed_ft(mover)
        add_movement_allowance(mover, bonus)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="dash",
            actor_id=mover.instance_id,
            actor_name=mover.template.name,
            distance_before_ft=battlefield.distance_ft,
            distance_after_ft=battlefield.distance_ft,
            movement_ft=bonus,
            animation="dash",
            description=f"{mover.template.name} takes the Dash action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Dash resolution failed for %s.", mover.template.name)
        raise RuntimeError("Dash could not be resolved.") from exc
