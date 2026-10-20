"""Source-neutral failed-save margin and duration resolution."""
from __future__ import annotations

import logging

from app.combat.dice import DiceProvider, roll_dice
from app.domain.models import DiceRoll
from app.domain.weapons import OnHitConditionSave

logger = logging.getLogger(__name__)


def escalation_duration(
    effect: OnHitConditionSave,
    save_roll: DiceRoll | None,
    succeeded: bool,
    dice: DiceProvider,
) -> tuple[bool, int | None]:
    """Compute one shared duration without consulting source display names."""
    try:
        rule = effect.failure_margin_escalation
        escalated = (
            not succeeded and save_roll is not None and rule is not None
            and save_roll.total <= effect.dc - rule.margin
        )
        duration = effect.duration_rounds
        if escalated and rule.replacement_duration_dice_count is not None:
            duration = roll_dice(
                dice, rule.replacement_duration_dice_count,
                rule.replacement_duration_dice_size,
            ) * rule.replacement_duration_round_multiplier
        if escalated and duration is None:
            raise ValueError("Escalated timed conditions require a source-declared duration.")
        return escalated, duration
    except Exception:
        logger.exception("Failed to evaluate declarative saving-throw escalation.")
        raise
