from __future__ import annotations

from app.domain.models import CombatantState


def speed_multiplier(state: CombatantState) -> float:
    result = 1.0
    for effect in state.timed_effects:
        result *= effect.speed_multiplier
    return result


def reactions_blocked(state: CombatantState) -> bool:
    return any(effect.blocks_reactions for effect in state.timed_effects)


def action_bonus_exclusive(state: CombatantState) -> bool:
    return any(effect.action_bonus_exclusive for effect in state.timed_effects)


def max_attacks_per_turn(state: CombatantState) -> int | None:
    limits = [
        effect.max_attacks_per_turn for effect in state.timed_effects
        if effect.max_attacks_per_turn is not None
    ]
    return min(limits) if limits else None
