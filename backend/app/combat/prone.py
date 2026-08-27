from __future__ import annotations

import logging

from app.combat.conditions import has_condition, remove_condition
from app.combat.movement_state import movement_locked, spend_movement
from app.domain.models import BattleEvent, CombatantState, ConditionType

logger = logging.getLogger(__name__)


def stand_from_prone(
    sequence: int,
    round_number: int,
    state: CombatantState,
) -> BattleEvent | None:
    try:
        if not has_condition(state, ConditionType.PRONE) or state.template.speed_ft == 0:
            return None
        if movement_locked(state):
            return None
        movement_cost = state.template.speed_ft // 2
        if state.movement_remaining_ft < movement_cost:
            return None
        spend_movement(state, movement_cost)
        remove_condition(state, ConditionType.PRONE)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="condition",
            actor_id=state.instance_id,
            actor_name=state.template.name,
            condition=ConditionType.PRONE,
            condition_active=False,
            movement_ft=movement_cost,
            animation="stand",
            description=f"{state.template.name} stands up, ending Prone.",
        )
    except Exception as exc:
        logger.exception("Failed to stand %s from Prone.", state.template.name)
        raise RuntimeError("Standing from Prone could not be resolved.") from exc
