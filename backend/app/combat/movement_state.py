from __future__ import annotations

from app.domain.models import CombatantState, ConditionType

_ZERO_SPEED = {
    ConditionType.GRAPPLED,
    ConditionType.PARALYZED,
    ConditionType.RESTRAINED,
}


def movement_locked(state: CombatantState) -> bool:
    return any(item.condition in _ZERO_SPEED for item in state.conditions)


def current_speed_ft(state: CombatantState) -> int:
    return 0 if movement_locked(state) else state.template.speed_ft


def begin_movement_budget(state: CombatantState) -> None:
    state.movement_allowance_ft = state.template.speed_ft
    state.movement_spent_ft = 0
    refresh_movement_budget(state)


def refresh_movement_budget(state: CombatantState) -> None:
    if movement_locked(state):
        state.movement_remaining_ft = 0
        return
    state.movement_remaining_ft = max(
        0,
        state.movement_allowance_ft - state.movement_spent_ft,
    )


def spend_movement(state: CombatantState, amount_ft: int) -> None:
    if amount_ft < 0:
        raise ValueError("Movement spent cannot be negative.")
    if amount_ft > state.movement_remaining_ft:
        raise ValueError("Movement exceeds the remaining movement budget.")
    state.movement_spent_ft += amount_ft
    state.movement_remaining_ft -= amount_ft


def add_movement_allowance(state: CombatantState, amount_ft: int) -> None:
    if amount_ft < 0:
        raise ValueError("Movement allowance cannot be negative.")
    state.movement_allowance_ft += amount_ft
    refresh_movement_budget(state)
