from __future__ import annotations

import logging

from app.combat.resources import action_resource_available, spend_action_resource
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
_RESOURCE_ID = "legendary-resistance"


def use_legendary_resistance(state: CombatantState) -> bool:
    """Spend one source-defined Legendary Resistance use after a failed save."""
    try:
        if not any(item.id == _RESOURCE_ID for item in state.template.resources):
            return False
        if not action_resource_available(state, _RESOURCE_ID):
            return False
        spend_action_resource(state, _RESOURCE_ID)
        return True
    except Exception as exc:
        logger.exception("Legendary Resistance failed for %s.", state.template.name)
        raise RuntimeError("Legendary Resistance could not be resolved.") from exc
