from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def pooled_healing_capacity(
    target: EncounterCombatant,
    cap_numerator: int,
    cap_denominator: int,
) -> int:
    """Return healing allowed before a source-defined fraction-of-max-HP ceiling."""
    try:
        if cap_numerator <= 0 or cap_denominator <= 0 or cap_numerator > cap_denominator:
            raise ValueError("Pooled-healing HP cap must be a positive fraction no greater than 1.")
        ceiling = effective_max_hp(target.state) * cap_numerator // cap_denominator
        return max(0, ceiling - target.state.current_hp)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to calculate pooled-healing capacity for %s.",
            target.state.template.name,
        )
        raise RuntimeError("Pooled-healing capacity could not be calculated.") from exc


def resolve_pooled_healing(
    targets: tuple[EncounterCombatant, ...],
    pool: int,
    *,
    cap_numerator: int,
    cap_denominator: int,
) -> tuple[list[tuple[EncounterCombatant, int]], int]:
    """Spend one shared healing pool across ordered legal targets."""
    try:
        if pool <= 0:
            raise ValueError("Pooled healing requires a positive healing pool.")
        if not targets:
            raise ValueError("Pooled healing requires at least one target.")

        remaining = pool
        allocations: list[tuple[EncounterCombatant, int]] = []
        for target in targets:
            if remaining <= 0:
                break
            capacity = pooled_healing_capacity(target, cap_numerator, cap_denominator)
            amount = min(remaining, capacity)
            if amount <= 0:
                continue
            restored = restore_hit_points(target.state, amount)
            if restored <= 0:
                continue
            allocations.append((target, restored))
            remaining -= restored
        return allocations, remaining
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Universal pooled-healing resolution failed.")
        raise RuntimeError("Pooled healing could not be resolved.") from exc
