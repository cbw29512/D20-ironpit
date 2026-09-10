from __future__ import annotations

import logging

from app.domain.models import CombatantState, ResourceDefinition, ResourceState

logger = logging.getLogger(__name__)


def resource_state(state: CombatantState, resource_id: str) -> ResourceState:
    try:
        matches = [resource for resource in state.resources if resource.id == resource_id]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one runtime resource {resource_id!r} on {state.template.name}; found {len(matches)}."
            )
        return matches[0]
    except Exception:
        logger.exception("Failed to resolve resource %s for %s.", resource_id, state.template.name)
        raise


def resource_definition(state: CombatantState, resource_id: str) -> ResourceDefinition:
    try:
        matches = [resource for resource in state.template.resources if resource.id == resource_id]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one resource definition {resource_id!r} on {state.template.name}; found {len(matches)}."
            )
        return matches[0]
    except Exception:
        logger.exception("Failed to resolve resource definition %s for %s.", resource_id, state.template.name)
        raise


def resolved_resource_id(resource_id: str | None, fallback_resource_id: str | None = None) -> str | None:
    """Resolve an action's explicit resource before any legacy/inferred fallback."""
    return resource_id if resource_id is not None else fallback_resource_id


def resource_available(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    try:
        if resource_id is None:
            return True
        if cost < 1:
            raise ValueError("Resource cost must be positive.")
        return resource_state(state, resource_id).current_uses >= cost
    except Exception:
        logger.exception("Failed to check resource %s availability for %s.", resource_id, state.template.name)
        raise


def action_resource_available(
    state: CombatantState,
    resource_id: str | None,
    cost: int = 1,
    *,
    fallback_resource_id: str | None = None,
) -> bool:
    """Shared availability check for attacks, saves, spells, bonus actions, and reactions."""
    return resource_available(state, resolved_resource_id(resource_id, fallback_resource_id), cost)


def is_recharge_resource(state: CombatantState, resource_id: str | None) -> bool:
    try:
        if resource_id is None:
            return False
        return resource_definition(state, resource_id).recharge is not None
    except Exception:
        logger.exception("Failed to identify recharge resource %s for %s.", resource_id, state.template.name)
        raise


def spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> int | None:
    try:
        if resource_id is None:
            return None
        if cost < 1:
            raise ValueError("Resource cost must be positive.")
        resource = resource_state(state, resource_id)
        if resource.current_uses < cost:
            raise ValueError(f"Resource {resource_id!r} does not have {cost} use(s) available.")
        resource.current_uses -= cost
        return resource.current_uses
    except Exception:
        logger.exception("Failed to spend resource %s for %s.", resource_id, state.template.name)
        raise


def spend_action_resource(
    state: CombatantState,
    resource_id: str | None,
    cost: int = 1,
    *,
    fallback_resource_id: str | None = None,
) -> int | None:
    """Shared resource spend path for every action family."""
    return spend_resource(state, resolved_resource_id(resource_id, fallback_resource_id), cost)
