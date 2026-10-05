from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def timed_armor_class_bonus(state: CombatantState) -> int:
    """Sum armor-class bonuses or penalties declared on active timed control limits."""
    try:
        return sum(
            effect.control_limits.armor_class_bonus
            for effect in state.timed_effects
            if effect.control_limits is not None
        )
    except Exception:
        logger.exception("Failed to resolve timed armor-class bonus for %s.", state.template.name)
        raise


def timed_saving_throw_flat_bonus(state: CombatantState, ability: str | None) -> int:
    """Sum ability-scoped timed save flats; unscoped lookups include every printed bonus."""
    try:
        wanted = str(ability or "").strip().casefold()
        total = 0
        for effect in state.timed_effects:
            limits = effect.control_limits
            if limits is None:
                continue
            for bonus in limits.saving_throw_flat_bonuses:
                if not wanted or bonus.ability == wanted:
                    total += bonus.flat_bonus
        return total
    except Exception:
        logger.exception(
            "Failed to resolve timed saving-throw flat bonus for %s / %s.",
            state.template.name,
            ability,
        )
        raise
