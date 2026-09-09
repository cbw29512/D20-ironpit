from __future__ import annotations

from app.domain.actions import SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.traits import CombatTrait


def evasion_applies(state: CombatantState, action: SavingThrowAction) -> bool:
    """2024 Evasion applies only to Dex saves that normally deal half damage on success."""
    return (
        CombatTrait.EVASION in state.template.combat_traits
        and action.save_ability == "dexterity"
        and action.success_damage == "half"
    )


def evasion_damage_fraction(state: CombatantState, action: SavingThrowAction, succeeded: bool) -> tuple[int, int] | None:
    if not evasion_applies(state, action):
        return None
    return (0, 1) if succeeded else (1, 2)
