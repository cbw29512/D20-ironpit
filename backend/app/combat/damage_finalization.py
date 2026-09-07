from __future__ import annotations

from typing import TypeVar

from app.combat.concentration import resolve_concentration_damage
from app.combat.dice import DiceProvider
from app.combat.source_bound_effects import end_damage_sensitive_effects
from app.domain.models import CombatantState

OutcomeT = TypeVar("OutcomeT", bound=str)


def finish_damage(
    state: CombatantState,
    outcome: OutcomeT,
    damage_taken: int,
    dice: DiceProvider | None,
    affected_states: list[CombatantState] | None,
) -> OutcomeT:
    """Finalize generic post-damage effects after HP state has been resolved."""
    end_damage_sensitive_effects(state)
    if state.concentration is None:
        return outcome
    if dice is None:
        if state.is_dead or state.is_unconscious:
            from app.combat.concentration import end_concentration_if_incapacitated

            end_concentration_if_incapacitated(state, affected_states)
            return outcome
        raise ValueError("A dice provider is required to resolve Concentration damage.")
    resolve_concentration_damage(state, damage_taken, dice, affected_states)
    return outcome
