"""Locked Iron Pit policy: wall creation is not a combat Action.

This is source-verified arena availability, not a new combat mechanic.
Cards keep the original spell/source metadata for reference; the automated
Action selector must skip wall creation even when the wall would deal damage.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Only wall-creation effects verified in the 2014/2024 project source.
# Do not infer new combat mechanics or future spells from their names.
ARENA_UNAVAILABLE_WALL_EFFECT_IDS = frozenset({
    "wall-of-ice",
    "wall-of-fire",
    "wall-of-stone",
})


def is_arena_unavailable_wall_effect(action_id: str) -> bool:
    """Return source-data availability; no Action, slot or resource is spent."""
    try:
        if not isinstance(action_id, str):
            raise TypeError("Wall availability lookup needs a source Action id.")
        return action_id in ARENA_UNAVAILABLE_WALL_EFFECT_IDS
    except Exception:
        logger.exception("Could not classify wall Action availability: %r.", action_id)
        raise
