from __future__ import annotations

import logging

from app.combat.healing_restore import restore_hit_points
from app.domain.runtime import CombatantState
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


def absorb_typed_damage(
    target: CombatantState,
    amount: int,
    damage_type: DamageType,
) -> bool:
    """Convert matching typed damage into Hit Point restoration."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if damage_type not in target.template.damage_absorption_types:
            return False
        restore_hit_points(target, amount)
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Typed damage absorption failed for %s.", target.template.name)
        raise RuntimeError("Typed damage absorption could not be resolved.") from exc
