from __future__ import annotations

import logging

from app.combat.resources import resource_available, spend_resource
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_save_success_override(state: CombatantState) -> str | None:
    """Spend one declared override to turn a failed saving throw into a success."""
    try:
        for grant in state.template.save_success_overrides:
            if not resource_available(state, grant.resource_id, grant.resource_cost):
                continue
            spend_resource(state, grant.resource_id, grant.resource_cost)
            return grant.source_id
        return None
    except Exception:
        logger.exception("Failed save-success override for %s.", state.template.name)
        raise
