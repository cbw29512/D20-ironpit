from __future__ import annotations

import logging

from app.combat.movement_state import movement_locked, refresh_movement_budget, spend_movement
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
    ConditionType.RESTRAINED,
}


def condition_states(state: CombatantState, condition: ConditionType) -> list[ConditionState]:
    return [item for item in state.conditions if item.condition is condition]


def condition_state(state: CombatantState, condition: ConditionType) -> ConditionState | None:
    return next(iter(condition_states(state, condition)), None)


def has_condition(state: CombatantState, condition: ConditionType) -> bool:
    return bool(condition_states(state, condition))


def apply_condition(
    state: CombatantState,
    condition: ConditionType,
    source: CombatantState | None = None,
    escape_dc: int | None = None,
    expires_on: ConditionExpiry | None = None,
    effect_id: str | None = None,
    linked_object_id: str | None = None,
) -> bool:
    try:
        if condition not in _SUPPORTED:
            raise ValueError(f"Condition is not fully implemented: {condition}")
        if condition in state.template.condition_immunities:
            return False
        if condition is ConditionType.GRAPPLED and (source is None or escape_dc is None):
            raise ValueError("Grappled requires a source and escape DC.")
        if condition is ConditionType.FRIGHTENED and source is None:
            raise ValueError("Frightened requires a fear source.")

        source_id = source.instance_id if source else None
        existing = next((
            item for item in condition_states(state, condition)
            if item.source_id == source_id
            and item.effect_id == effect_id
            and item.linked_object_id == linked_object_id
            and item.escape_dc == escape_dc
        ), None)
        if existing is not None:
            existing.expires_on = expires_on
            return False

        state.conditions.append(ConditionState(
            condition=condition,
            source_id=source_id,
            source_name=source.template.name if source else None,
            effect_id=effect_id,
            linked_object_id=linked_object_id,
            escape_dc=escape_dc,
            expires_on=expires_on,
        ))
        refresh_movement_budget(state)
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply %s to %s.", condition, state.template.name)
        raise RuntimeError("Condition could not be applied.") from exc


def remove_condition(state: CombatantState, condition: ConditionType) -> bool:
    before = len(state.conditions)
    state.conditions = [item for item in state.conditions if item.condition is not condition]
    changed = len(state.conditions) != before
    if changed:
        refresh_movement_budget(state)
    return changed


def remove_condition_instance(
    state: CombatantState,
    condition: ConditionType,
    linked_object_id: str | None = None,
    source_id: str | None = None,
) -> bool:
    before = len(state.conditions)
    state.conditions = [
        item for item in state.conditions
        if not (
            item.condition is condition
            and (linked_object_id is None or item.linked_object_id == linked_object_id)
            and (source_id is None or item.source_id == source_id)
        )
    ]
    changed = len(state.conditions) != before
    if changed:
        refresh_movement_budget(state)
    return changed


def can_willingly_approach(state: CombatantState, target_id: str) -> bool:
    return not any(
        item.source_id == target_id
        for item in condition_states(state, ConditionType.FRIGHTENED)
    )


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
