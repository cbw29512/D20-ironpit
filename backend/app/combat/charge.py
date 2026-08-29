from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import CombatantState, DamageType, WeaponAttack
from app.domain.size import CreatureSize, size_at_most
from app.domain.traits import CombatTrait


@dataclass(frozen=True)
class ChargeProfile:
    attack_id: str
    minimum_move_ft: int
    dice_count: int
    dice_size: int
    damage_type: DamageType
    max_target_size: CreatureSize


_PROFILES = {
    "boar-gore": ChargeProfile(
        "boar-gore", 20, 1, 6, DamageType.PIERCING, CreatureSize.MEDIUM,
    ),
    "elk-ram": ChargeProfile(
        "elk-ram", 20, 1, 6, DamageType.BLUDGEONING, CreatureSize.LARGE,
    ),
    "giant-boar-gore": ChargeProfile(
        "giant-boar-gore", 20, 2, 6, DamageType.PIERCING, CreatureSize.LARGE,
    ),
}


def charge_profile(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    movement_ft: int,
) -> ChargeProfile | None:
    """Return a charge rider only when the complete 2024 trigger is satisfied."""
    if CombatTrait.CHARGE not in attacker.template.combat_traits:
        return None
    profile = _PROFILES.get(attack.id)
    if profile is None or movement_ft < profile.minimum_move_ft:
        return None
    if not size_at_most(defender.template.size, profile.max_target_size):
        return None
    return profile


def charge_can_close(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    distance_ft: int,
) -> bool:
    profile = _PROFILES.get(attack.id)
    if CombatTrait.CHARGE not in attacker.template.combat_traits or profile is None:
        return False
    movement_needed = max(0, distance_ft - attack.weapon.reach_ft)
    return (
        movement_needed >= profile.minimum_move_ft
        and movement_needed <= attacker.movement_remaining_ft
        and size_at_most(defender.template.size, profile.max_target_size)
    )
