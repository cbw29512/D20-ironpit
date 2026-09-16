from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.models import CombatantState, DiceRoll
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


def _resource(state: CombatantState):
    return next((item for item in state.resources if item.id == "indomitable"), None)


def use_indomitable(state: CombatantState, ability: str, dice: DiceProvider) -> DiceRoll | None:
    """Reroll a failed save; edition data decides whether the reroll gets an extra bonus."""
    try:
        bonus = state.template.progression_features.indomitable_bonus
        resource = _resource(state)
        if resource is None or resource.current_uses <= 0:
            return None
        if ability not in state.template.saving_throw_bonuses:
            raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
        resource.current_uses -= 1
        roll = apply_d20_bonus_dice(
            state,
            ModifierKind.SAVING_THROW_BONUS_DIE,
            roll_d20(
                dice,
                state.template.saving_throw_bonuses[ability] + bonus,
                saving_throw_mode(state, ability),
            ),
            dice,
        )
        suffix = f" +{bonus}" if bonus else ""
        return roll.model_copy(update={"notation": f"{roll.notation} [Indomitable{suffix}]"})
    except Exception:
        logger.exception("Indomitable resolution failed for %s.", state.template.name)
        raise
