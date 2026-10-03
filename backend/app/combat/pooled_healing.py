from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def bind_pool_healing_action(healer: EncounterCombatant, target: EncounterCombatant, action: HealingAction) -> HealingAction:
    """Select the useful finite-pool allocation without mutating source or fight state."""
    try:
        if not action.healing_from_resource_pool:
            return action
        resource = next((item for item in healer.state.resources if item.id == action.resource_id), None)
        amount = min(resource.current_uses if resource else 0, pooled_healing_capacity(target, 1, 1))
        if amount <= 0:
            raise ValueError("Pool healing requires available points and missing HP.")
        return action.model_copy(update={"healing_bonus": amount, "resource_cost": amount})
    except Exception:
        logger.exception("Failed to bind healing pool %s for %s -> %s.", action.id, healer.combatant_id, target.combatant_id)
        raise


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
