from __future__ import annotations

import logging

from app.domain.models import CombatantState, ConditionKind

logger = logging.getLogger(__name__)


def is_incapacitated(state: CombatantState) -> bool:
    try:
        return ConditionKind.INCAPACITATED in state.conditions
    except Exception as exc:
        logger.exception("Failed to read Incapacitated state for %s.", state.template.name)
        raise RuntimeError("Condition state could not be resolved.") from exc


def require_activity(state: CombatantState, activity: str) -> None:
    """Reject an Action, Bonus Action, or Reaction while Incapacitated."""
    try:
        if is_incapacitated(state):
            raise ValueError(f"Incapacitated creatures cannot take a {activity}.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to validate %s permission for %s.", activity, state.template.name)
        raise RuntimeError("Activity permission could not be resolved.") from exc
