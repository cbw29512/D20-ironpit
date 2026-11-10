"""Generic HP-pool allocation: no save roll, spell name, or source ID dispatch."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
_MAX_SAFE_INT = 9007199254740991  # Keep browser Number integer parity.


@dataclass(frozen=True, slots=True)
class PoolCandidate:
    """Caller computes eligibility from its immutable source and live fight state."""

    combatant_id: str
    current_hp: int
    eligible: bool = True


def allocate_hit_point_pool(
    rolled_pool: int, candidates: list[PoolCandidate],
) -> tuple[list[str], int]:
    """Spend pool in ascending HP order; ties preserve caller's declared order.

    Zero-HP and ineligible candidates cannot be selected or spend pool.
    Never mutate creature HP, source cards, or the candidates themselves.
    """
    try:
        if type(rolled_pool) is not int or not 0 <= rolled_pool <= _MAX_SAFE_INT:
            raise ValueError("HP pool must be a nonnegative browser-safe integer.")
        if not isinstance(candidates, list):
            raise TypeError("HP pool candidates must be a list.")
        seen: set[str] = set()
        for candidate in candidates:
            if not isinstance(candidate, PoolCandidate):
                raise TypeError("HP pool entries must be PoolCandidate data.")
            if not isinstance(candidate.combatant_id, str) or not candidate.combatant_id.strip():
                raise ValueError("HP pool candidate requires a nonempty combatant ID.")
            if candidate.combatant_id in seen:
                raise ValueError("HP pool candidate IDs must be unique.")
            seen.add(candidate.combatant_id)
            if type(candidate.current_hp) is not int or not 0 <= candidate.current_hp <= _MAX_SAFE_INT:
                raise ValueError("HP pool candidate HP must be a nonnegative browser-safe integer.")
            if type(candidate.eligible) is not bool:
                raise ValueError("HP pool eligibility must be boolean.")
        remaining = rolled_pool
        affected: list[str] = []
        for candidate in sorted(candidates, key=lambda item: item.current_hp):
            if not candidate.eligible or candidate.current_hp == 0:
                continue
            if candidate.current_hp > remaining:
                break
            remaining -= candidate.current_hp
            affected.append(candidate.combatant_id)
        return affected, remaining
    except Exception:
        logger.exception("Universal hit-point-pool allocation failed.")
        raise
