from __future__ import annotations

import logging

from app.domain.models import CombatantState
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def note_incoming_damage_types(state: CombatantState, damage_types: set[DamageType] | set[str]) -> None:
    """Remember damage types that landed since the last Regeneration check."""
    try:
        if state.template.regeneration is None or not damage_types:
            return
        remembered = set(state.damage_types_taken_since_regen)
        remembered.update(str(item) for item in damage_types)
        state.damage_types_taken_since_regen = sorted(remembered)
    except Exception:
        logger.exception("Failed to record Regeneration damage types for %s.", state.template.name)
        raise


def delay_zero_hp_death(state: CombatantState) -> bool:
    """Printed Regeneration can keep a creature alive at 0 HP until its next turn."""
    try:
        trait = state.template.regeneration
        return bool(trait is not None and trait.survives_zero_until_turn and not state.is_dead)
    except Exception:
        logger.exception("Failed to evaluate delayed Regeneration death for %s.", state.template.name)
        raise
