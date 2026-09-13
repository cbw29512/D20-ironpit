from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def effective_max_hp(state: CombatantState) -> int:
    """Return the current Hit Point maximum after temporary increases and reductions."""
    try:
        return max(0, state.template.max_hp + state.max_hp_bonus - state.max_hp_reduction)
    except Exception:
        logger.exception("Failed to calculate effective max HP for %s.", state.template.name)
        raise
