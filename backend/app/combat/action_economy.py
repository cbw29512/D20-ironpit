from __future__ import annotations

from typing import Literal

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_effect_rules import action_bonus_exclusive, reactions_blocked
from app.domain.models import CombatantState

ActionCost = Literal["action", "bonus_action", "reaction"]


def is_available(state: CombatantState, cost: ActionCost) -> bool:
    """Return whether the printed action type is currently available."""
    if state.is_dead or is_incapacitated(state):
        return False
    if state.turn_terminated and cost != "reaction":
        return False
    if cost == "reaction":
        return state.reaction_available and not reactions_blocked(state)
    if cost == "action":
        if action_bonus_exclusive(state) and not state.bonus_action_available:
            return False
        return state.action_available
    if action_bonus_exclusive(state) and not state.action_available:
        return False
    return state.bonus_action_available


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
