from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import _mark_dead
from app.domain.models import CombatantState, DamageRollComponent, WeaponAttack


def apply_max_hp_reduction(state: CombatantState, amount: int) -> int:
    """Apply an in-combat maximum-HP reduction and return the amount actually removed."""
    if amount < 0:
        raise ValueError("Maximum-HP reduction cannot be negative.")
    if amount == 0 or state.is_dead:
        return 0
    before = effective_max_hp(state)
    state.max_hp_reduction = min(state.template.max_hp + state.max_hp_bonus, state.max_hp_reduction + amount)
    after = effective_max_hp(state)
    state.current_hp = min(state.current_hp, after)
    if after == 0:
        _mark_dead(state)
    return before - after


def apply_attack_max_hp_reduction(
    state: CombatantState, attack: WeaponAttack, damage_components: list[DamageRollComponent],
) -> int:
    """Apply an attack drain from post-defense damage, optionally scoped to one damage type."""
    rider = attack.max_hp_reduction
    if rider is None:
        return 0
    amount = sum(
        part.applied_total or 0
        for part in damage_components
        if rider.damage_type is None or part.damage_type == rider.damage_type
    )
    return apply_max_hp_reduction(state, amount)
