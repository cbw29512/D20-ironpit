from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageType
from app.domain.traits import CombatTrait


def resolve_undead_fortitude(
    state: CombatantState,
    damage_taken: int,
    damage_types: set[DamageType],
    *,
    critical: bool,
    dice: DiceProvider | None,
) -> bool:
    """Resolve SRD 5.2.1 Undead Fortitude after lethal damage reaches 0 HP."""
    if CombatTrait.UNDEAD_FORTITUDE not in state.template.combat_traits:
        return False
    if critical or DamageType.RADIANT in damage_types:
        return False
    if dice is None:
        raise ValueError("Undead Fortitude requires a dice provider for its Constitution saving throw.")
    bonus = state.template.saving_throw_bonuses.get("constitution")
    if bonus is None:
        raise ValueError(f"{state.template.name} lacks a Constitution saving throw bonus.")
    dc = 5 + damage_taken
    if dice.roll(20) + bonus < dc:
        return False
    state.current_hp = 1
    state.is_alive = True
    state.is_dead = False
    state.is_unconscious = False
    state.is_stable = False
    return True
