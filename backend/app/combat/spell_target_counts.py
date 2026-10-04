from __future__ import annotations

import logging

from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def spell_save_target_count(action: SpellSaveAction, slot_level: int) -> int:
    """Return the printed target cap at the expended slot, including extra targets per slot above."""
    try:
        if action.level == 0:
            return action.target_count
        if slot_level < action.level:
            raise ValueError(f"Illegal slot level {slot_level} for {action.name}.")
        extra = (slot_level - action.level) * action.target_count_per_slot_above
        return action.target_count + extra
    except Exception:
        logger.exception("Failed to scale save-spell targets for %s.", action.id)
        raise
