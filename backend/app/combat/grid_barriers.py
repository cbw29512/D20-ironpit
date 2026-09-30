from __future__ import annotations

import logging

from app.domain.grid import GridPosition
from app.domain.persistent_barriers import PersistentBarrierState

logger = logging.getLogger(__name__)


def barrier_blocks_transition(
    origin: GridPosition,
    destination: GridPosition,
    barriers: list[PersistentBarrierState] | None,
) -> bool:
    """Return True when a live movement-blocking barrier owns this orthogonal grid edge."""
    try:
        if not barriers:
            return False
        if abs(origin.x - destination.x) + abs(origin.y - destination.y) != 1:
            return False
        key = tuple(sorted(((origin.x, origin.y), (destination.x, destination.y))))
        for barrier in barriers:
            if not barrier.blocks_movement:
                continue
            for section in barrier.sections:
                if section.destroyed or section.current_hp <= 0:
                    continue
                if any(edge.canonical_key() == key for edge in section.edges):
                    return True
        return False
    except Exception:
        logger.exception(
            "Failed to evaluate persistent barrier passage from %s to %s.",
            origin,
            destination,
        )
        raise
