from __future__ import annotations

from typing import Literal

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantState

ActionCost = Literal["action", "bonus_action", "reaction"]


def is_available(state: CombatantState, cost: ActionCost) -> bool:
    """Return whether the printed action type is currently available under the 2024 economy."""
    if state.is_dead or is_incapacitated(state):
        return False
    if cost == "action":
        return state.action_available
    if cost == "bonus_action":
        return state.bonus_action_available
    return state.reaction_available


def spend(state: CombatantState, cost: ActionCost) -> None:
    """Spend exactly one Action, Bonus Action, or Reaction; fail closed if unavailable."""
    if not is_available(state, cost):
        raise ValueError(f"{cost.replace('_', ' ').title()} is not available.")
    if cost == "action":
        state.action_available = False
    elif cost == "bonus_action":
        state.bonus_action_available = False
    else:
        state.reaction_available = False
