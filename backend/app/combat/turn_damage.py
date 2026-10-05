from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def note_single_type_turn_damage(
    state: CombatantState,
    amount: int,
    damage_types: set,
) -> None:
    """Accumulate one applied damage packet by type for source-owned same-turn triggers."""
    try:
        if amount <= 0 or len(damage_types) != 1:
            return
        damage_type = next(iter(damage_types))
        key = damage_type.value if hasattr(damage_type, "value") else str(damage_type)
        state.damage_taken_this_turn_by_type[key] = state.damage_taken_this_turn_by_type.get(key, 0) + amount
    except Exception:
        logger.exception("Failed to record same-turn typed damage for %s.", state.template.name)
        raise


def clear_turn_damage(setup: EncounterSetup) -> None:
    """Clear damage accumulated during the just-ended active turn."""
    try:
        for member in [*setup.heroes, *setup.monsters]:
            member.state.damage_taken_this_turn_by_type = {}
    except Exception:
        logger.exception("Failed to clear per-turn typed damage state.")
        raise
