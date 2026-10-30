from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def healing_prevented(state: CombatantState) -> bool:
    try:
        return any(
            modifier.kind is ModifierKind.HEALING_PREVENTED
            for modifier in state.active_modifiers
        )
    except Exception as exc:
        logger.exception("Failed healing-prevention check for %s.", state.template.name)
        raise RuntimeError("Healing-prevention state could not be evaluated.") from exc


def restore_hit_points(state: CombatantState, amount: int) -> int:
    """Restore true HP unless a universal rule currently prevents healing."""
    try:
        if amount < 0:
            raise ValueError("Healing cannot be negative.")
        if (
            state.is_dead
            or amount == 0
            or CombatTrait.SWARM in state.template.combat_traits
            or healing_prevented(state)
        ):
            return 0
        before = state.current_hp
        state.current_hp = min(effective_max_hp(state), before + amount)
        healed = state.current_hp - before
        if healed > 0:
            state.is_alive = True
            state.is_unconscious = False
            state.is_stable = False
            state.death_save_successes = 0
            state.death_save_failures = 0
        return healed
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed HP restoration for %s.", state.template.name)
        raise RuntimeError("Hit Points could not be restored.") from exc
