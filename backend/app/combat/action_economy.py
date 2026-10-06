from __future__ import annotations

import logging
from typing import Literal

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_effect_control import suppresses_action, suppresses_bonus_action, suppresses_reactions
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
ActionCost = Literal["action", "bonus_action", "reaction"]
VoluntaryActivity = Literal["movement", "action", "bonus_action"]


def single_activity_restricted(state: CombatantState) -> bool:
    return any(effect.turn_behavior == "single_activity" for effect in state.timed_effects)


def action_bonus_exclusive(state: CombatantState) -> bool:
    try:
        return any(
            effect.control_limits is not None and effect.control_limits.action_bonus_exclusive
            for effect in state.timed_effects
        )
    except Exception:
        logger.exception("Failed to resolve action/bonus exclusivity for %s.", state.template.name)
        raise


def voluntary_activity_available(state: CombatantState, activity: VoluntaryActivity) -> bool:
    if single_activity_restricted(state):
        return state.voluntary_turn_activity in {None, activity}
    if action_bonus_exclusive(state) and activity in {"action", "bonus_action"}:
        return state.voluntary_turn_activity in {None, activity}
    return True


def claim_voluntary_activity(state: CombatantState, activity: VoluntaryActivity) -> None:
    if single_activity_restricted(state):
        if state.voluntary_turn_activity not in {None, activity}:
            raise ValueError("A different voluntary turn activity is already committed.")
        state.voluntary_turn_activity = activity
        if activity == "movement":
            state.action_available = False
            state.bonus_action_available = False
        elif activity == "action":
            state.bonus_action_available = False
            state.movement_remaining_ft = 0
        else:
            state.action_available = False
            state.movement_remaining_ft = 0
        return
    if action_bonus_exclusive(state) and activity in {"action", "bonus_action"}:
        if state.voluntary_turn_activity not in {None, activity}:
            raise ValueError("Action and Bonus Action cannot both be used under this effect.")
        state.voluntary_turn_activity = activity
        if activity == "action":
            state.bonus_action_available = False
        else:
            state.action_available = False


def is_available(state: CombatantState, cost: ActionCost) -> bool:
    """Return whether the printed action type is currently available under the 2024 economy."""
    if state.is_dead or is_incapacitated(state):
        return False
    if state.turn_terminated and cost != "reaction":
        return False
    if cost == "action":
        return state.action_available and not suppresses_action(state) and voluntary_activity_available(state, "action")
    if cost == "bonus_action":
        return state.bonus_action_available and not suppresses_bonus_action(state) and voluntary_activity_available(state, "bonus_action")
    if suppresses_reactions(state):
        return False
    return state.reaction_available


def spend(state: CombatantState, cost: ActionCost) -> None:
    """Spend exactly one Action, Bonus Action, or Reaction; fail closed if unavailable."""
    if not is_available(state, cost):
        raise ValueError(f"{cost.replace('_', ' ').title()} is not available.")
    if cost == "action":
        claim_voluntary_activity(state, "action")
        state.action_available = False
    elif cost == "bonus_action":
        claim_voluntary_activity(state, "bonus_action")
        state.bonus_action_available = False
    else:
        state.reaction_available = False