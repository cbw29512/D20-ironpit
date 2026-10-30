"""Universal hit-point pool allocation for spells such as 2014 Sleep.

The spell supplies pool dice and exclusions; the engine only spends the
rolled pool in ascending current-HP order. No source-name dispatch.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PoolCandidate:
    combatant_id: str
    current_hp: int
    eligible: bool = True


def allocate_hit_point_pool(
    rolled_pool: int, candidates: list[PoolCandidate],
) -> tuple[list[str], int]:
    """Return affected combatant IDs and unspent HP pool.

    Ineligible creatures do not consume any pool. The first eligible creature
    that cannot be fully covered stops allocation, per 2014 Sleep.
    """
    try:
        if type(rolled_pool) is not int or rolled_pool < 0:
            raise ValueError("HP pool must be a nonnegative integer.")
        ids = [item.combatant_id for item in candidates]
        if len(set(ids)) != len(ids):
            raise ValueError("HP-pool target IDs must be unique.")
        if any(type(item.current_hp) is not int or item.current_hp < 0 for item in candidates):
            raise ValueError("HP-pool targets require nonnegative integer current HP.")
        remaining = rolled_pool
        affected: list[str] = []
        for item in sorted(candidates, key=lambda row: (row.current_hp, row.combatant_id)):
            if not item.eligible or item.current_hp == 0:
                continue
            if item.current_hp > remaining:
                break
            remaining -= item.current_hp
            affected.append(item.combatant_id)
        return affected, remaining
    except Exception:
        logger.exception("Universal HP-pool allocation failed.")
        raise
