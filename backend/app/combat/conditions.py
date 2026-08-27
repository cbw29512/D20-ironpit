from __future__ import annotations

import logging

from app.domain.models import BattleEvent, CombatantState, ConditionState, ConditionType

logger = logging.getLogger(__name__)
_SUPPORTED = {ConditionType.PRONE}


def has_condition(state: CombatantState, condition: ConditionType) -> bool:
    return any(item.condition is condition for item in state.conditions)


def apply_condition(
    state: CombatantState,
    condition: ConditionType,
    source: CombatantState | None = None,
) -> bool:
    try:
        if condition not in _SUPPORTED:
            raise ValueError(f"Condition is not fully implemented: {condition}")
        if condition in state.template.condition_immunities or has_condition(state, condition):
            return False
        state.conditions.append(ConditionState(
            condition=condition,
            source_id=source.template.id if source else None,
            source_name=source.template.name if source else None,
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


def attack_condition_sources(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
) -> tuple[int, int]:
    try:
        advantage = 0
        disadvantage = 0
        if has_condition(attacker, ConditionType.PRONE):
            disadvantage += 1
        if has_condition(defender, ConditionType.PRONE):
            if distance_ft <= 5:
                advantage += 1
            else:
                disadvantage += 1
        return advantage, disadvantage
    except Exception as exc:
        logger.exception("Failed to resolve condition attack modifiers.")
        raise RuntimeError("Condition attack modifiers could not be resolved.") from exc


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
            actor_id=state.template.id,
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
