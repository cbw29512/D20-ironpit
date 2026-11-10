"""Reusable fight-state facts for source-owned timed self buffs.

Card fields describe size and D20 qualification. Engine resolution reads only
live timed effects; immutable monster templates are never modified.
"""
from __future__ import annotations

import logging

from app.domain.runtime import CombatantState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def active_timed_self_buff_actions(state: CombatantState):
    """Find self buffs backed by a live owner-linked timed-effect group."""
    try:
        active_ids = {
            effect.source_effect_id for effect in state.timed_effects
            if effect.source_id and effect.source_effect_id
        }
        return [
            action for action in state.template.timed_self_buff_actions
            if action.id in active_ids
        ]
    except Exception:
        logger.exception("Failed active timed buff lookup for %s.", state.template.name)
        raise


def timed_check_advantage_sources(state: CombatantState, ability: str | None) -> int:
    """Count generic active grants scoped to a particular ability check."""
    try:
        if ability is None:
            return 0
        return sum(
            ability in action.ability_check_advantage_abilities
            for action in active_timed_self_buff_actions(state)
        )
    except Exception:
        logger.exception("Failed timed check Advantage for %s / %s.",
                         state.template.name, ability)
        raise


def effective_creature_size(state: CombatantState) -> CreatureSize:
    """Return current size, not the original source card's immutable size."""
    try:
        sizes = [
            action.size_override for action in active_timed_self_buff_actions(state)
            if action.size_override is not None
        ]
        # Different simultaneous shape overrides require an explicit layering
        # policy. Do not guess which one wins.
        if len(set(sizes)) > 1:
            raise ValueError(f"Conflicting timed size overrides for {state.template.name}.")
        return sizes[0] if sizes else state.template.size
    except Exception:
        logger.exception("Failed effective timed creature size for %s.", state.template.name)
        raise
