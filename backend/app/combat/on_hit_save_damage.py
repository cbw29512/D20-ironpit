from __future__ import annotations

from dataclasses import dataclass

from app.combat.damage import roll_damage_component
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.models import CombatantState, DamageRollComponent, DiceRoll, WeaponAttack


@dataclass(frozen=True)
class OnHitSaveDamageResolution:
    component: DamageRollComponent | None = None
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None


def resolve_on_hit_save_damage(
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
) -> OnHitSaveDamageResolution:
    effect = attack.on_hit_save_damage
    if effect is None:
        return OnHitSaveDamageResolution()
    save_roll, succeeded = resolve_saving_throw(defender, effect.save_ability, effect.dc, dice)
    if succeeded and effect.success_damage == "none":
        return OnHitSaveDamageResolution(None, save_roll, effect.save_ability, effect.dc, True)
    component = roll_damage_component(
        dice, effect.source, effect.dice_count, effect.dice_size,
        effect.damage_bonus, effect.damage_type, critical=False,
    )
    if succeeded and effect.success_damage == "half":
        component = component.model_copy(update={"total": component.total // 2})
    return OnHitSaveDamageResolution(component, save_roll, effect.save_ability, effect.dc, succeeded)
