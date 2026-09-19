from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def resource_state(state: CombatantState, resource_id: str):
    return next((item for item in state.resources if item.id == resource_id), None)


def resource_available(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    try:
        if resource_id is None:
            return True
        if resource_id in state.template.unlimited_resource_ids:
            return True
        resource = resource_state(state, resource_id)
        return resource is not None and resource.current_uses >= cost
    except Exception as exc:
        logger.exception("Failed to check resource %r for %s.", resource_id, state.template.name)
        raise RuntimeError("Resource availability could not be resolved.") from exc


def spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> int | None:
    try:
        if resource_id is None or resource_id in state.template.unlimited_resource_ids:
            return None
        resource = resource_state(state, resource_id)
        if resource is None or resource.current_uses < cost:
            raise ValueError(f"Resource {resource_id!r} is unavailable.")
        resource.current_uses -= cost
        return resource.current_uses
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to spend resource %r for %s.", resource_id, state.template.name)
        raise RuntimeError("Resource spending could not be resolved.") from exc


def action_resource_available(state: CombatantState, action) -> bool:
    return resource_available(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))


def spend_action_resource(state: CombatantState, action) -> int | None:
    return spend_resource(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))
