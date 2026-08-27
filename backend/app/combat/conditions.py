from __future__ import annotations

import logging

from app.domain.models import (
    BattleEvent,
    CombatantState,
    ConditionExpiry,
    ConditionState,
    ConditionType,
)

logger = logging.getLogger(__name__)
_SUPPORTED = {
    ConditionType.PRONE,
    ConditionType.GRAPPLED,
    ConditionType.POISONED,
    ConditionType.FRIGHTENED,
    ConditionType.PARALYZED,
}


def condition_state(state: CombatantState, condition: ConditionType) -> ConditionState | None:
    return next((item for item in state.conditions if item.condition is condition), None)


def has_condition(state: CombatantState, condition: ConditionType) -> bool:
    return condition_state(state, condition) is not None


def apply_condition(
    state: CombatantState,
    condition: ConditionType,
    source: CombatantState | None = None,
    escape_dc: int | None = None,
    expires_on: ConditionExpiry | None = None,
) -> bool:
    try:
        if condition not in _SUPPORTED:
            raise ValueError(f"Condition is not fully implemented: {condition}")
        if condition in state.template.condition_immunities or has_condition(state, condition):
            return False
        if condition is ConditionType.GRAPPLED and (source is None or escape_dc is None):
            raise ValueError("Grappled requires a source and escape DC.")
        if condition is ConditionType.FRIGHTENED and source is None:
            raise ValueError("Frightened requires a fear source.")
        state.conditions.append(ConditionState(
            condition=condition,
            source_id=source.instance_id if source else None,
            source_name=source.template.name if source else None,
            escape_dc=escape_dc,
            expires_on=expires_on,
        ))
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply %s to %s.", condition, state.template.name)
        raise RuntimeError("Condition could not be applied.") from exc


def remove_condition(state: CombatantState, condition: ConditionType) -> bool:
    before = len(state.conditions)
    state.conditions = [item for item in state.conditions if item.condition is not condition]
    return len(state.conditions) != before


def can_willingly_approach(state: CombatantState, target_id: str) -> bool:
    frightened = condition_state(state, ConditionType.FRIGHTENED)
    return frightened is None or frightened.source_id != target_id


def stand_from_prone(
    sequence: int,
    round_number: int,
    state: CombatantState,
) -> BattleEvent | None:
    try:
        if not has_condition(state, ConditionType.PRONE) or state.template.speed_ft == 0:
            return None
        movement_cost = state.template.speed_ft // 2
        if state.movement_remaining_ft < movement_cost:
            return None
        state.movement_remaining_ft -= movement_cost
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
