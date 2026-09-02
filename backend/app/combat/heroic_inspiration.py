from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DiceRoll, RollMode

logger = logging.getLogger(__name__)


def grant_heroic_warrior_inspiration(state: CombatantState) -> bool:
    """Grant one Heroic Inspiration at turn start when Heroic Warrior lacks it."""
    try:
        if not state.template.progression_features.heroic_warrior or state.heroic_inspiration:
            return False
        state.heroic_inspiration = True
        return True
    except Exception as exc:
        logger.exception("Heroic Warrior turn-start grant failed for %s.", state.template.name)
        raise RuntimeError("Heroic Warrior inspiration could not be granted.") from exc


def _standalone_hit(natural: int, modifier: int, target_ac: int) -> bool:
    return natural != 1 and (natural == 20 or natural + modifier >= target_ac)


def _reroll_index(roll: DiceRoll, target_ac: int) -> int | None:
    if roll.selected_roll is None:
        raise ValueError("Heroic Inspiration requires a selected d20 roll.")
    if _standalone_hit(roll.selected_roll, roll.modifier, target_ac):
        return None
    if roll.mode is RollMode.NORMAL:
        if len(roll.rolls) != 1:
            raise ValueError("Normal d20 roll must contain exactly one die.")
        return 0
    if len(roll.rolls) != 2:
        raise ValueError("Advantage or Disadvantage d20 roll must contain exactly two dice.")
    if roll.mode is RollMode.ADVANTAGE:
        return 0 if roll.rolls[0] <= roll.rolls[1] else 1
    if roll.mode is RollMode.DISADVANTAGE:
        lower = 0 if roll.rolls[0] <= roll.rolls[1] else 1
        other = 1 - lower
        return lower if _standalone_hit(roll.rolls[other], roll.modifier, target_ac) else None
    raise ValueError(f"Unsupported d20 roll mode for Heroic Inspiration: {roll.mode}.")


def reroll_failed_attack_with_heroic_inspiration(
    state: CombatantState,
    roll: DiceRoll,
    target_ac: int,
    dice: DiceProvider,
) -> tuple[DiceRoll, bool]:
    """Spend Inspiration on the first recoverable missed attack and replace exactly one d20."""
    try:
        if not state.heroic_inspiration:
            return roll, False
        index = _reroll_index(roll, target_ac)
        if index is None:
            return roll, False
        rerolled = list(roll.rolls)
        rerolled[index] = dice.roll(20)
        if roll.mode is RollMode.ADVANTAGE:
            selected = max(rerolled)
        elif roll.mode is RollMode.DISADVANTAGE:
            selected = min(rerolled)
        else:
            selected = rerolled[0]
        state.heroic_inspiration = False
        return roll.model_copy(update={
            "rolls": rerolled,
            "selected_roll": selected,
            "total": selected + roll.modifier,
            "notation": f"{roll.notation} [Heroic Inspiration]",
        }), True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Heroic Inspiration attack reroll failed for %s.", state.template.name)
        raise RuntimeError("Heroic Inspiration reroll could not be resolved.") from exc
