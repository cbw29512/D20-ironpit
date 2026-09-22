from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def refresh_start_of_turn_resources(state: CombatantState) -> None:
    """Refill declaratively listed resources at the start of the owner's turn."""
    try:
        for resource_id in state.template.progression_features.start_of_turn_resource_refresh_ids:
            resource = next((item for item in state.resources if item.id == resource_id), None)
            if resource is None:
                raise ValueError(f"Start-of-turn refresh references missing resource {resource_id}.")
            resource.current_uses = resource.max_uses
    except Exception as exc:
        logger.exception("Failed start-of-turn resource refresh for %s.", state.template.name)
        raise RuntimeError("Start-of-turn resource refresh could not be resolved.") from exc
