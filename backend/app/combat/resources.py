from __future__ import annotations

from typing import Any, NamedTuple

from app.combat.dice import DiceProvider
from app.domain.runtime import CombatantState, ResourceState


class RechargeResult(NamedTuple):
    resource_id: str
    roll: int
    recharged: bool


def resource_state(state: CombatantState, resource_id: str) -> ResourceState | None:
    return next((item for item in state.resources if item.id == resource_id), None)


def can_spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    if resource_id is None:
        return True
    resource = resource_state(state, resource_id)
    return resource is not None and resource.current_uses >= cost


def can_use_action_resource(state: CombatantState, action: Any) -> bool:
    return can_spend_resource(
        state,
        getattr(action, "resource_id", None),
        getattr(action, "resource_cost", 1),
    )


def spend_action_resource(state: CombatantState, action: Any) -> int | None:
    resource_id = getattr(action, "resource_id", None)
    if resource_id is None:
        return None
    cost = getattr(action, "resource_cost", 1)
    resource = resource_state(state, resource_id)
    if resource is None or resource.current_uses < cost:
        raise ValueError(f"Resource {resource_id} is unavailable for {getattr(action, 'id', 'action')}.")
    resource.current_uses -= cost
    return resource.current_uses


def refresh_recharge_resources(state: CombatantState, dice: DiceProvider) -> list[RechargeResult]:
    """At monster turn start, roll only depleted abilities that declare Recharge."""
    if state.template.kind != "monster":
        return []
    recharge_definitions = {
        item.id: item
        for item in state.template.resources
        if item.recharge_minimum is not None
    }
    if not recharge_definitions:
        return []
    results: list[RechargeResult] = []
    for resource in state.resources:
        definition = recharge_definitions.get(resource.id)
        if definition is None or resource.current_uses >= resource.max_uses:
            continue
        roll = dice.roll(definition.recharge_die_size)
        recharged = roll >= definition.recharge_minimum
        if recharged:
            resource.current_uses = resource.max_uses
        results.append(RechargeResult(resource.id, roll, recharged))
    return results
