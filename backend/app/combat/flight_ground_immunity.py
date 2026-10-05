from __future__ import annotations

import logging

from app.combat.effective_movement_modes import effective_movement_modes
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def combatant_is_flying(state: CombatantState) -> bool:
    """True when the combatant has an effective Fly speed. Horizontal fly stays fly."""
    try:
        modes = state.template.movement_modes
        if hasattr(modes, "model_copy"):
            return effective_movement_modes(state).fly_ft > 0
        printed = 0
        if isinstance(modes, dict):
            printed = int(modes.get("fly_ft") or 0)
        return printed > 0
    except Exception:
        logger.exception("Failed flying check for %s.", state.template.name)
        raise


def flying_counters_ground_contact(state: CombatantState, *, ground_contact: bool) -> bool:
    """Flying is only a buff that prevents ground-contact debuffs from landing."""
    try:
        return bool(ground_contact) and combatant_is_flying(state)
    except Exception:
        logger.exception("Failed ground-contact flying counter for %s.", state.template.name)
        raise


def resolve_flight_countered_ground_conditions(state: CombatantState) -> list[tuple[str, str, int]]:
    """Start-of-turn: an active flying buff clears already-present ground-contact debuffs."""
    try:
        if not combatant_is_flying(state):
            return []
        from app.combat.timed_condition_lifecycle import remove_effect_group

        resolved: list[tuple[str, str, int]] = []
        for effect in list(state.timed_effects):
            if not effect.ground_contact:
                continue
            removed = remove_effect_group(state, effect)
            for condition_id in removed:
                resolved.append((condition_id, effect.source_id, 0))
        return resolved
    except Exception:
        logger.exception("Failed to clear ground-contact debuffs for flyer %s.", state.template.name)
        raise
