from __future__ import annotations

from dataclasses import dataclass, field

from app.combat.condition_immunity import condition_is_immune
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll, WeaponAttack
from app.domain.size import size_at_most


@dataclass(frozen=True)
class OnHitSaveResolution:
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied_condition: str | None = None
    damage_components: list[DamageRollComponent] = field(default_factory=list)
    damage_total: int = 0
    applied_conditions: list[str] = field(default_factory=list)


def _eligible(defender: CombatantState, effect) -> bool:
    creature_type = (defender.template.creature_type or "").lower()
    subtypes = {item.lower() for item in defender.template.creature_subtypes}
    return creature_type not in effect.excluded_creature_types and not subtypes.intersection(effect.excluded_creature_subtypes)


def _save_damage(defender, attack, dice, succeeded, affected_states):
    effect = attack.on_hit_save_effect
    if effect is None or effect.damage_dice_count == 0 or effect.damage_type is None: return [], 0
    rolls = [dice.roll(effect.damage_dice_size) for _ in range(effect.damage_dice_count)]
    total = max(0, sum(rolls) + effect.damage_bonus)
    if succeeded: total = total // 2 if effect.success_damage == "half" else 0
    component = DamageRollComponent(source=f"{attack.weapon.name} save rider", notation=f"{effect.damage_dice_count}d{effect.damage_dice_size}+{effect.damage_bonus}", rolls=rolls, modifier=effect.damage_bonus, damage_type=DamageType(effect.damage_type), total=total)
    applied_total, adjusted = apply_damage_defenses(defender, [component], attack=attack)
    if applied_total:
        apply_damage(defender, applied_total, critical=False, damage_types={DamageType(effect.damage_type)}, dice=dice, affected_states=affected_states)
    return adjusted, applied_total


def _apply_stable_zero_hp(defender, attack, source_id, round_number, affected_states) -> list[str]:
    effect = attack.on_hit_save_effect
    if effect is None or not effect.zero_hp_stable or defender.current_hp != 0: return []
    if source_id is None or round_number is None: raise ValueError("Stable zero-HP rider requires source and round context.")
    defender.is_alive = True; defender.is_dead = False; defender.is_unconscious = True; defender.is_stable = True
    defender.death_save_successes = 0; defender.death_save_failures = 0
    applied: list[str] = []
    for condition_id in effect.zero_hp_condition_ids:
        result = apply_timed_condition(
            defender, condition_id, source_id, source_effect_id=attack.id,
            applied_round=round_number, expires_round=round_number + effect.zero_hp_duration_rounds,
            expiry_timing="source_turn_start", affected_states=affected_states,
        )
        if result: applied.append(result)
    return applied


def resolve_on_hit_save(
    defender: CombatantState, attack: WeaponAttack, dice: DiceProvider, *, source_id: str | None = None,
    round_number: int | None = None, affected_states: list[CombatantState] | None = None,
) -> OnHitSaveResolution:
    effect = attack.on_hit_save_effect
    if effect is None or defender.is_dead or not defender.is_alive or not _eligible(defender, effect): return OnHitSaveResolution()
    if effect.max_target_size is not None and not size_at_most(defender.template.size, effect.max_target_size): return OnHitSaveResolution()
    roll, succeeded = resolve_saving_throw(defender, effect.save_ability, effect.dc, dice)
    damage_components, damage_total = _save_damage(defender, attack, dice, succeeded, affected_states)
    zero_hp_conditions = _apply_stable_zero_hp(defender, attack, source_id, round_number, affected_states) if damage_total else []
    applied = None
    if effect.condition_id is not None and not succeeded and defender.is_alive and not defender.is_dead and not condition_is_immune(defender, effect.condition_id):
        timed = effect.duration_rounds is not None or effect.repeat_save_timing is not None or effect.ends_on_damage
        if timed:
            if source_id is None or round_number is None: raise ValueError("Timed on-hit save effects require source_id and round_number.")
            applied = apply_timed_condition(
                defender, effect.condition_id, source_id, source_effect_id=attack.id, applied_round=round_number,
                expires_round=round_number + effect.duration_rounds if effect.duration_rounds is not None else None,
                repeat_save_ability=effect.save_ability if effect.repeat_save_timing is not None else None,
                repeat_save_dc=effect.dc if effect.repeat_save_timing is not None else None,
                repeat_save_timing=effect.repeat_save_timing, affected_states=affected_states, ends_on_damage=effect.ends_on_damage,
            )
        else:
            if effect.condition_id not in defender.active_effect_ids: defender.active_effect_ids.append(effect.condition_id)
            applied = effect.condition_id
    all_conditions = [*zero_hp_conditions, *([applied] if applied else [])]
    return OnHitSaveResolution(roll, effect.save_ability, effect.dc, succeeded, applied, damage_components, damage_total, list(dict.fromkeys(all_conditions)))