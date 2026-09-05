from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.actions import SavingThrowAction
from app.domain.runtime import CombatantState


def resource_available(state: CombatantState, action: SavingThrowAction) -> bool:
    if action.resource_id is None:
        return True
    resource = next((item for item in state.resources if item.id == action.resource_id), None)
    return resource is not None and resource.current_uses >= action.resource_cost


def consume_resource(state: CombatantState, action: SavingThrowAction) -> int | None:
    if action.resource_id is None:
        return None
    resource = next((item for item in state.resources if item.id == action.resource_id), None)
    if resource is None or resource.current_uses < action.resource_cost:
        raise ValueError(f"{action.name} has no remaining resource use.")
    resource.current_uses -= action.resource_cost
    return resource.current_uses


def recharge_start_of_turn(state: CombatantState, dice: DiceProvider) -> None:
    by_id = {item.id: item for item in state.resources}
    for definition in state.template.resources:
        threshold = definition.recharge_min_d6
        resource = by_id.get(definition.id)
        if threshold is None or resource is None or resource.current_uses >= resource.max_uses:
            continue
        if dice.roll(6) >= threshold:
            resource.current_uses = resource.max_uses
