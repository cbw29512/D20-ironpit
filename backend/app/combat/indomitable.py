from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.models import CombatantState, DiceRoll
from app.domain.modifiers import ModifierKind


def _resource(state: CombatantState):
    return next((item for item in state.resources if item.id == "indomitable"), None)


def use_indomitable(
    state: CombatantState,
    ability: str,
    dice: DiceProvider,
    *,
    magical: bool = False,
    advantage_sources: int = 0,
) -> DiceRoll | None:
    """Resolve the RAW reroll after policy has already chosen to spend Indomitable."""
    bonus = state.template.progression_features.indomitable_bonus
    resource = _resource(state)
    if bonus <= 0 or resource is None or resource.current_uses <= 0:
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
            saving_throw_mode(state, ability, magical=magical, advantage_sources=advantage_sources),
        ),
        dice,
    )
    return roll.model_copy(update={"notation": f"{roll.notation} [Indomitable +{bonus}]"})
