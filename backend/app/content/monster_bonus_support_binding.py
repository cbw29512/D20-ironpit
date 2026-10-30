from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def runtime_bonus_support(template: CombatantTemplate, base_name: str) -> bool:
    try:
        return any(
            action.name == base_name and action.action_cost == "bonus_action"
            for action in template.support_actions
        )
    except Exception as exc:
        logger.exception("Failed to inspect support Bonus Action binding for %s.", template.id)
        raise RuntimeError("Support Bonus Action binding could not be evaluated.") from exc
