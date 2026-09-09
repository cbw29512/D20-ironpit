from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import DamageRollComponent, DamageType, SavingThrowAction

logger = logging.getLogger(__name__)


def _damage_rolls(
    action: SavingThrowAction,
    dice: DiceProvider,
    shared_damage_rolls: list[int] | None,
) -> list[int]:
    try:
        if shared_damage_rolls is None:
            return [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)]
        if len(shared_damage_rolls) != action.damage_dice_count:
            raise ValueError(f"{action.name} shared damage roll count does not match its damage dice.")
        if any(not 1 <= roll <= action.damage_dice_size for roll in shared_damage_rolls):
            raise ValueError(f"{action.name} shared damage rolls contain an invalid die result.")
        return list(shared_damage_rolls)
    except Exception:
        logger.exception("Failed damage-roll preparation for save action %s.", action.id)
        raise


def build_save_damage_components(
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | None = None,
    capture_shared_damage_rolls: list[int] | None = None,
) -> list[DamageRollComponent]:
    try:
        if action.damage_dice_count == 0:
            return []
        needs_shared_roll = capture_shared_damage_rolls is not None
        if succeeded and action.success_damage == "none" and not needs_shared_roll:
            return []
        if action.damage_type is None:
            raise ValueError(f"{action.name} has damage dice but no damage type.")
        rolls = _damage_rolls(action, dice, shared_damage_rolls)
        if capture_shared_damage_rolls is not None:
            capture_shared_damage_rolls.clear()
            capture_shared_damage_rolls.extend(rolls)
        if succeeded and action.success_damage == "none":
            return []
        total = sum(rolls) + action.damage_bonus
        if succeeded and action.success_damage == "half":
            total //= 2
        return [DamageRollComponent(
            source=action.name,
            notation=f"{action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus}",
            rolls=rolls,
            modifier=action.damage_bonus,
            damage_type=DamageType(action.damage_type),
            total=max(0, total),
        )]
    except Exception:
        logger.exception("Failed damage-component preparation for save action %s.", action.id)
        raise
