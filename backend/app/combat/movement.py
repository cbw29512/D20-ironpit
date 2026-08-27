from __future__ import annotations

import logging

from app.combat.conditions import can_willingly_approach
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
        mover.movement_remaining_ft -= moved
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


def take_dash(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    battlefield: BattlefieldState,
) -> BattleEvent:
    """Spend the Action to gain extra movement equal to current Speed for this turn."""
    try:
        if not mover.action_available:
            raise ValueError("Action is not available for Dash.")
        mover.action_available = False
        mover.movement_remaining_ft += mover.template.speed_ft
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="dash",
            actor_id=mover.instance_id,
            actor_name=mover.template.name,
            distance_before_ft=battlefield.distance_ft,
            distance_after_ft=battlefield.distance_ft,
            movement_ft=mover.template.speed_ft,
            animation="dash",
            description=f"{mover.template.name} takes the Dash action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Dash resolution failed for %s.", mover.template.name)
        raise RuntimeError("Dash could not be resolved.") from exc
