from __future__ import annotations

import logging

from app.combat.conditions import has_condition
from app.combat.dice import DiceProvider
from app.combat.movement_state import spend_movement
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, ConditionType

logger = logging.getLogger(__name__)


def move_away_from_target(
    sequence: int,
    round_number: int,
    mover: CombatantState,
    reactor: CombatantState,
    battlefield: BattlefieldState,
    movement_ft: int,
    dice: DiceProvider,
    reactor_can_see_mover: bool = True,
) -> list[BattleEvent]:
    """Spend voluntary movement away, resolving any OA before reach is crossed."""
    try:
        if movement_ft < 0:
            raise ValueError("Retreat movement cannot be negative.")
        planned = min(movement_ft, mover.movement_remaining_ft)
        if planned <= 0:
            return []

        intended_after = battlefield.distance_ft + planned
        events = resolve_opportunity_attack(
            sequence,
            round_number,
            reactor,
            mover,
            battlefield,
            intended_after,
            dice,
            mover_visible=reactor_can_see_mover,
        )
        if not mover.is_alive:
            return events
        if has_condition(mover, ConditionType.PRONE):
            return events

        moved = min(planned, mover.movement_remaining_ft)
        if moved <= 0:
            return events
        before = battlefield.distance_ft
        battlefield.distance_ft += moved
        spend_movement(mover, moved)
        events.append(BattleEvent(
            sequence=sequence + len(events),
            round_number=round_number,
            event_type="movement",
            actor_id=mover.instance_id,
            actor_name=mover.template.name,
            target_id=reactor.instance_id,
            target_name=reactor.template.name,
            distance_before_ft=before,
            distance_after_ft=battlefield.distance_ft,
            movement_ft=moved,
            animation="retreat",
            description=f"{mover.template.name} moves {moved} feet away.",
        ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Retreat movement failed for %s.", mover.template.name)
        raise RuntimeError("Retreat movement could not be resolved.") from exc
