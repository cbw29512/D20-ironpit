from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import DiceRoll, RollMode

logger = logging.getLogger(__name__)


def resolve_roll_mode(advantage_sources: int = 0, disadvantage_sources: int = 0) -> RollMode:
    """Collapse any number of advantage/disadvantage sources into one RAW roll mode."""
    try:
        has_advantage = advantage_sources > 0
        has_disadvantage = disadvantage_sources > 0
        if has_advantage == has_disadvantage:
            return RollMode.NORMAL
        return RollMode.ADVANTAGE if has_advantage else RollMode.DISADVANTAGE
    except Exception as exc:
        logger.exception("Failed to resolve d20 roll mode.")
        raise RuntimeError("D20 roll mode could not be resolved.") from exc


def attack_roll_hits(natural: int, total: int, target_ac: int) -> bool:
    """Resolve the universal attack-roll hit rule: natural 1 misses, natural 20 hits, otherwise total vs. AC."""
    return natural != 1 and (natural == 20 or total >= target_ac)


def roll_d20(dice: DiceProvider, modifier: int = 0, mode: RollMode = RollMode.NORMAL) -> DiceRoll:
    """Roll an auditable d20 check, preserving both dice when advantage/disadvantage applies."""
    try:
        rolls = [dice.roll(20)] if mode is RollMode.NORMAL else [dice.roll(20), dice.roll(20)]
        if mode is RollMode.ADVANTAGE:
            selected = max(rolls)
        elif mode is RollMode.DISADVANTAGE:
            selected = min(rolls)
        else:
            selected = rolls[0]
        return DiceRoll(
            notation="1d20" if mode is RollMode.NORMAL else "2d20",
            rolls=rolls,
            modifier=modifier,
            selected_roll=selected,
            mode=mode,
            total=selected + modifier,
        )
    except Exception as exc:
        logger.exception("Failed to resolve d20 roll in %s mode.", mode)
        raise RuntimeError("D20 roll could not be completed.") from exc
