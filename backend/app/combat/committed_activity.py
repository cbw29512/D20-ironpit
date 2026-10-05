from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def committed_activity_active(state: CombatantState) -> bool:
    """Return whether the creature is currently performing a committed timed activity."""
    try:
        return bool(state.delayed_resource_refills)
    except Exception:
        logger.exception("Failed committed-activity check.")
        raise RuntimeError("Committed activity state could not be read.") from None
