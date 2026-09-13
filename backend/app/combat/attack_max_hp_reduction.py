from __future__ import annotations

from app.combat.max_hp_reduction import apply_max_hp_reduction
from app.domain.events import DamageRollComponent
from app.domain.runtime import CombatantState
from app.domain.weapons import WeaponAttack


def resolve_attack_max_hp_reduction(
    attack: WeaponAttack,
    target: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[int | None, int | None]:
    """Apply a configured max-HP rider from post-defense damage components."""
    rider = attack.max_hp_reduction_on_hit
    if rider is None:
        return None, None
    amount = sum(
        component.applied_total
        for component in components
        if rider.damage_type is None or component.damage_type is rider.damage_type
    )
    return apply_max_hp_reduction(target, amount)
