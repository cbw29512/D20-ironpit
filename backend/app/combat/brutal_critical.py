from __future__ import annotations

from app.domain.combatants import DamageType, WeaponAttack
from app.domain.runtime import CombatantState
from app.domain.weapons import WeaponAttackKind


def brutal_critical_bonus_damage(
    state: CombatantState,
    attack: WeaponAttack,
    critical: bool,
) -> tuple[str, int, int, DamageType] | None:
    """Return 2014 Barbarian extra weapon dice for a critical melee hit."""
    dice_count = state.template.progression_features.brutal_critical_dice
    if not critical or dice_count <= 0 or attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
        return None
    return "Brutal Critical", dice_count, attack.weapon.dice_size, attack.weapon.damage_type
