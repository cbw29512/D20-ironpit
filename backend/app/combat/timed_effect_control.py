from __future__ import annotations

from app.domain.models import CombatantState


def suppresses_action(state: CombatantState) -> bool:
    return any(effect.suppress_action for effect in state.timed_effects)


def suppresses_bonus_action(state: CombatantState) -> bool:
    return any(effect.suppress_bonus_action for effect in state.timed_effects)


def suppresses_reactions(state: CombatantState) -> bool:
    return any(effect.suppress_reactions for effect in state.timed_effects)


def suppresses_movement(state: CombatantState) -> bool:
    return any(effect.suppress_movement for effect in state.timed_effects)


def suppresses_voluntary_turn(state: CombatantState) -> bool:
    return suppresses_action(state) and suppresses_bonus_action(state) and suppresses_movement(state)
