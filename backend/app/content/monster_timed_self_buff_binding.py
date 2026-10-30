from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def runtime_timed_self_buff(
    template: CombatantTemplate,
    name: str,
    action_cost: str,
) -> bool:
    try:
        return any(
            action.name.strip().lower() == name.strip().lower()
            and action.action_cost == action_cost
            for action in template.timed_self_buff_actions
        )
    except Exception as exc:
        logger.exception("Failed timed self-buff binding check for %s.", template.id)
        raise RuntimeError("Timed self-buff binding could not be evaluated.") from exc


__all__ = ["runtime_timed_self_buff"]
