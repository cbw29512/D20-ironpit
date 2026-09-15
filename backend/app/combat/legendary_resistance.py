from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
LEGENDARY_RESISTANCE_RESOURCE_ID = "legendary-resistance"


def legendary_resistance_remaining(state: CombatantState) -> int:
    resource = next(
        (item for item in state.resources if item.id == LEGENDARY_RESISTANCE_RESOURCE_ID),
        None,
    )
    return 0 if resource is None else resource.current_uses


def use_legendary_resistance_on_failure(state: CombatantState) -> bool:
    """Spend one use whenever a failed saving throw can be converted to success."""
    try:
        resource = next(
            (item for item in state.resources if item.id == LEGENDARY_RESISTANCE_RESOURCE_ID),
            None,
        )
        if resource is None or resource.current_uses <= 0:
            return False
        resource.current_uses -= 1
        return True
    except Exception as exc:
        logger.exception("Legendary Resistance handling failed for %s.", state.template.name)
        raise RuntimeError("Legendary Resistance could not be resolved.") from exc
