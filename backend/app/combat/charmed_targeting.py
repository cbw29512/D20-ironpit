from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def charmed_source_ids(state: CombatantState) -> set[str]:
    """Return source combatant IDs of live Charmed conditions on the creature."""
    try:
        return {
            effect.source_id
            for effect in state.timed_effects
            if effect.effect_id == "charmed" and effect.source_id
        }
    except Exception:
        logger.exception("Failed to read Charmed sources for %s.", getattr(state.template, "name", "unknown"))
        raise


def charmed_blocks_hostile_target(actor: CombatantState, target_id: str) -> bool:
    """2024 Charmed: the creature cannot attack or harm the charmer."""
    try:
        return target_id in charmed_source_ids(actor)
    except Exception:
        logger.exception("Failed to evaluate Charmed targeting for %s.", getattr(actor.template, "name", "unknown"))
        raise
