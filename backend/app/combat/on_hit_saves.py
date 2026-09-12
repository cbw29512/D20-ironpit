from __future__ import annotations

from dataclasses import dataclass

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.models import CombatantState, DiceRoll, WeaponAttack
from app.domain.size import size_at_most


@dataclass(frozen=True)
class OnHitSaveResolution:
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied_condition: str | None = None


def resolve_on_hit_save(
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
) -> OnHitSaveResolution:
    effect = attack.on_hit_save_effect
    if effect is None or defender.is_dead or not defender.is_alive:
        return OnHitSaveResolution()
    if effect.max_target_size is not None and not size_at_most(defender.template.size, effect.max_target_size):
        return OnHitSaveResolution()
    roll, succeeded = resolve_saving_throw(defender, effect.save_ability, effect.dc, dice)
    applied = None
    if not succeeded and not condition_is_immune(defender, effect.condition_id):
        if effect.condition_id not in defender.active_effect_ids:
            defender.active_effect_ids.append(effect.condition_id)
        applied = effect.condition_id
    return OnHitSaveResolution(roll, effect.save_ability, effect.dc, succeeded, applied)
