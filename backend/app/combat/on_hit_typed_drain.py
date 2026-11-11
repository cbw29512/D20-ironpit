"""One source-neutral attack rider: typed damage -> maximum-HP loss and healing."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.restoration_riders import apply_hit_point_maximum_reduction_state
from app.combat.zero_hp import restore_hit_points
from app.domain.models import CombatantState, DamageRollComponent, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TypedDrainResult:
    damage_taken: int
    max_hp_reduced: int
    attacker_healed: int
    killed_by_zero_maximum: bool


def apply_on_hit_typed_drain(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
) -> TypedDrainResult | None:
    """Use only the post-defense component matching the printed damage type."""
    try:
        spec = attack.on_hit_typed_drain
        if spec is None:
            return None
        amount = sum(
            component.applied_total or 0 for component in components
            if component.damage_type == spec.damage_type
        )
        if not amount:
            return TypedDrainResult(0, 0, 0, False)
        was_dead = defender.is_dead
        raw_maximum_after = (
            defender.template.max_hp + defender.max_hp_bonus
            - defender.hit_point_maximum_reduction - amount
        )
        reduction = (
            apply_hit_point_maximum_reduction_state(
                defender, amount, zero_max_hp_kills=spec.zero_maximum_hp_kills,
            ) if spec.reduce_target_maximum_hp else 0
        )
        healed = restore_hit_points(attacker, amount) if spec.heal_attacker else 0
        killed = bool(
            spec.zero_maximum_hp_kills and not was_dead and reduction
            and raw_maximum_after <= 0 and defender.is_dead
        )
        return TypedDrainResult(amount, reduction, healed, killed)
    except Exception:
        logger.exception("On-hit typed damage transfer failed for %s.", attack.id)
        raise
