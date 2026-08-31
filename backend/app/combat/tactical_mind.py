from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DiceRoll


def _second_wind(state: CombatantState):
    return next((item for item in state.resources if item.id == "second-wind"), None)


def tactical_mind_available(state: CombatantState) -> bool:
    level = state.template.level or 0
    resource = _second_wind(state)
    return bool(
        state.template.archetype.lower() == "fighter"
        and level >= 2
        and resource is not None
        and resource.current_uses > 0
    )


def apply_tactical_mind(
    state: CombatantState,
    failed_check: DiceRoll,
    dc: int,
    dice: DiceProvider,
) -> tuple[DiceRoll, bool, bool]:
    """Add Tactical Mind's d10 after failure; spend Second Wind only if it changes the result."""
    if failed_check.total >= dc or not tactical_mind_available(state):
        return failed_check, False, False
    bonus = dice.roll(10)
    updated = failed_check.model_copy(update={
        "notation": f"{failed_check.notation}+1d10",
        "rolls": [*failed_check.rolls, bonus],
        "total": failed_check.total + bonus,
    })
    succeeded = updated.total >= dc
    if succeeded:
        resource = _second_wind(state)
        if resource is None:
            raise ValueError("Second Wind resource disappeared during Tactical Mind.")
        resource.current_uses -= 1
    return updated, True, succeeded
