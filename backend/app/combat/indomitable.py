from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.models import CombatantState, DiceRoll
from app.domain.modifiers import ModifierKind


def _resource(state: CombatantState):
    return next((item for item in state.resources if item.id == "indomitable"), None)


def use_indomitable(state: CombatantState, ability: str, dice: DiceProvider) -> DiceRoll | None:
    """Resolve the edition-correct reroll after policy chooses to spend Indomitable."""
    progression = state.template.progression_features
    resource = _resource(state)
    if not progression.indomitable_reroll or resource is None or resource.current_uses <= 0:
        return None
    if ability not in state.template.saving_throw_bonuses:
        raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
    resource.current_uses -= 1
    bonus = progression.indomitable_bonus
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
