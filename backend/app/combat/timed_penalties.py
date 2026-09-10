from __future__ import annotations

from app.domain.runtime import CombatantState, TimedEffect

TIMED_PENALTY_EFFECT_ID = "timed-penalty"


def d20_disadvantage_sources(state: CombatantState, ability: str) -> int:
    return sum(1 for effect in state.timed_effects if effect.d20_disadvantage_ability == ability)


def damage_penalty_specs(state: CombatantState) -> list[tuple[int, int]]:
    return [
        (effect.damage_penalty_dice_count, effect.damage_penalty_dice_size)
        for effect in state.timed_effects if effect.damage_penalty_dice_count > 0
    ]


def apply_damage_roll_penalty(state: CombatantState, components: list, dice) -> list[int]:
    """Subtract each active penalty once from the attack's complete damage roll."""
    penalty_rolls: list[int] = []
    for count, size in damage_penalty_specs(state):
        penalty_rolls.extend(dice.roll(size) for _ in range(count))
    remaining = sum(penalty_rolls)
    for component in components:
        if remaining <= 0:
            break
        reduction = min(component.total, remaining)
        component.total -= reduction
        component.modifier -= reduction
        component.notation += f" - {reduction}"
        remaining -= reduction
    return penalty_rolls


def apply_timed_penalty(
    state: CombatantState, source_id: str, source_effect_id: str, *, round_number: int,
    d20_disadvantage_ability: str | None, damage_penalty_dice_count: int,
    damage_penalty_dice_size: int, repeat_save_ability: str, repeat_save_dc: int,
    repeat_save_timing: str, automatic_success_after_rounds: int | None,
) -> str:
    state.timed_effects = [effect for effect in state.timed_effects if not (
        effect.effect_id == TIMED_PENALTY_EFFECT_ID
        and effect.source_id == source_id and effect.source_effect_id == source_effect_id
    )]
    state.timed_effects.append(TimedEffect(
        effect_id=TIMED_PENALTY_EFFECT_ID, source_id=source_id, source_effect_id=source_effect_id,
        applied_round=round_number, repeat_save_ability=repeat_save_ability,
        repeat_save_dc=repeat_save_dc, repeat_save_timing=repeat_save_timing,
        repeat_save_eligible_round=round_number, d20_disadvantage_ability=d20_disadvantage_ability,
        damage_penalty_dice_count=damage_penalty_dice_count, damage_penalty_dice_size=damage_penalty_dice_size,
        automatic_success_round=(round_number + automatic_success_after_rounds if automatic_success_after_rounds else None),
    ))
    return TIMED_PENALTY_EFFECT_ID
