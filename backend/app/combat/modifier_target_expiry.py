from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def expire_target_turn_modifiers(state: CombatantState) -> int:
    """Expire modifiers due at the end of this affected creature turn."""
    try:
        before = len(state.active_modifiers)
        state.active_modifiers = [
            item for item in state.active_modifiers
            if not (
                item.expires_at_end_of_target_turn
                or (
                    item.expires_target_turn_serial is not None
                    and item.expires_target_turn_serial <= state.turn_serial
                )
            )
        ]
        return before - len(state.active_modifiers)
    except Exception:
        logger.exception("Failed target-turn modifier expiry for %s.", state.template.id)
        raise
