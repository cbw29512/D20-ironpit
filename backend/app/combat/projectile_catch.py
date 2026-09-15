from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.event_support import DamageRollComponent, DiceRoll
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind


def resolve_projectile_catch(
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
    dice,
) -> tuple[list[DamageRollComponent], DiceRoll | None, bool | None]:
    """Spend the defender's reaction to catch a matching ranged projectile on a successful save."""
    profile = defender.template.projectile_catch_reaction
    if profile is None or not is_available(defender, "reaction") or attack.weapon.attack_kind is not WeaponAttackKind.RANGED:
        return components, None, None
    if not any(part.damage_type == profile.damage_type and (part.applied_total or 0) > 0 for part in components):
        return components, None, None
    spend(defender, "reaction")
    roll, succeeded = resolve_saving_throw(defender, profile.save_ability, profile.save_dc, dice)
    if not succeeded:
        return components, roll, False
    caught = [
        part.model_copy(update={"applied_total": 0}) if part.damage_type == profile.damage_type else part
        for part in components
    ]
    return caught, roll, True
