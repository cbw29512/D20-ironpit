from __future__ import annotations

from typing import Literal

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantState

ActionCost = Literal["action", "bonus_action", "reaction"]


def _action_or_bonus_only(state: CombatantState) -> bool:
    return any(effect.action_or_bonus_only for effect in state.timed_effects)


def _reactions_disabled(state: CombatantState) -> bool:
    return any(effect.reactions_disabled for effect in state.timed_effects)


def is_available(state: CombatantState, cost: ActionCost) -> bool:
    """Return whether the printed action type is currently available under the 2024 economy."""
    if state.is_dead or is_incapacitated(state):
        return False
    if state.turn_terminated and cost != "reaction":
        return False
    if cost == "action":
        return state.action_available
    if cost == "bonus_action":
        return state.bonus_action_available
    if cost == "reaction":
        return state.reaction_available and not _reactions_disabled(state)
    raise ValueError(f"Unknown action cost: {cost}")


def spend(state: CombatantState, cost: ActionCost) -> None:
    """Spend one action type and enforce any active Action-or-Bonus-Action restriction."""
    if not is_available(state, cost):
        raise ValueError(f"{cost.replace('_', ' ').title()} is not available.")
    if cost == "action":
        state.action_available = False
        if _action_or_bonus_only(state):
            state.bonus_action_available = False
    elif cost == "bonus_action":
        state.bonus_action_available = False
        if _action_or_bonus_only(state):
            state.action_available = False
    else:
        state.reaction_available = False
