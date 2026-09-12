from __future__ import annotations

from dataclasses import dataclass

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
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
    *,
    source_id: str | None = None,
    round_number: int | None = None,
    affected_states: list[CombatantState] | None = None,
) -> OnHitSaveResolution:
    effect = attack.on_hit_save_effect
    if effect is None or defender.is_dead or not defender.is_alive:
        return OnHitSaveResolution()
    if effect.max_target_size is not None and not size_at_most(defender.template.size, effect.max_target_size):
        return OnHitSaveResolution()
    roll, succeeded = resolve_saving_throw(defender, effect.save_ability, effect.dc, dice)
    applied = None
    if not succeeded and not condition_is_immune(defender, effect.condition_id):
        timed = effect.duration_rounds is not None or effect.repeat_save_timing is not None or effect.ends_on_damage
        if timed:
            if source_id is None or round_number is None:
                raise ValueError("Timed on-hit save effects require source_id and round_number.")
            applied = apply_timed_condition(
                defender,
                effect.condition_id,
                source_id,
                source_effect_id=attack.id,
                applied_round=round_number,
                expires_round=round_number + effect.duration_rounds if effect.duration_rounds is not None else None,
                repeat_save_ability=effect.save_ability if effect.repeat_save_timing is not None else None,
                repeat_save_dc=effect.dc if effect.repeat_save_timing is not None else None,
                repeat_save_timing=effect.repeat_save_timing,
                affected_states=affected_states,
                ends_on_damage=effect.ends_on_damage,
            )
        else:
            if effect.condition_id not in defender.active_effect_ids:
                defender.active_effect_ids.append(effect.condition_id)
            applied = effect.condition_id
    return OnHitSaveResolution(roll, effect.save_ability, effect.dc, succeeded, applied)
