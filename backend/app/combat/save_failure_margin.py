from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import DiceRoll
from app.domain.on_hit_saves import OnHitSaveEffect


def failure_margin_conditions_and_duration(
    effect: OnHitSaveEffect,
    save_roll: DiceRoll | None,
    save_succeeded: bool,
    dice: DiceProvider,
) -> tuple[list[str], int | None]:
    """Resolve declarative failed-save escalation without monster-specific branches."""
    escalation = effect.failure_margin_escalation
    if escalation is None or save_succeeded or save_roll is None:
        return [], effect.duration_rounds
    if effect.dc - save_roll.total < escalation.margin:
        return [], effect.duration_rounds
    duration = effect.duration_rounds
    if escalation.replacement_duration_rounds is not None:
        duration = escalation.replacement_duration_rounds
    elif escalation.replacement_duration_dice_count:
        duration = sum(
            dice.roll(escalation.replacement_duration_dice_size)
            for _ in range(escalation.replacement_duration_dice_count)
        ) * escalation.replacement_duration_round_multiplier
    return list(escalation.additional_condition_ids), duration
