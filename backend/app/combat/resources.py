from __future__ import annotations

from app.domain.models import CombatantState


def resource_state(state: CombatantState, resource_id: str):
    return next((item for item in state.resources if item.id == resource_id), None)


def resource_definition(state: CombatantState, resource_id: str):
    return next((item for item in state.template.resources if item.id == resource_id), None)


def resource_available(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    if resource_id is None:
        return True
    resource = resource_state(state, resource_id)
    return resource is not None and resource.current_uses >= cost


def spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> int | None:
    if resource_id is None:
        return None
    resource = resource_state(state, resource_id)
    if resource is None or resource.current_uses < cost:
        raise ValueError(f"Resource {resource_id!r} is unavailable.")
    resource.current_uses -= cost
    return resource.current_uses


def action_resource_available(state: CombatantState, action) -> bool:
    return resource_available(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))


def spend_action_resource(state: CombatantState, action) -> int | None:
    return spend_resource(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))
