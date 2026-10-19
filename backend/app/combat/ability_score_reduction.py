"""Source-neutral fight-state ability-score reductions.

An immutable combatant card holds the base score. The existing fight-state
ability_score_reductions mapping holds cumulative, rest-removable reductions.
This is an effect primitive, not a monster-specific attack resolver.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.combat.instant_death import apply_instant_death
from app.domain.character_builds import AbilityName
from app.domain.runtime import CombatantState

ABILITIES = frozenset((
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
))


@dataclass(frozen=True)
class AbilityScoreReductionResult:
    ability: AbilityName
    score_before: int
    score_after: int
    applied: int
    death_outcome: str | None = None


def effective_ability_score(state: CombatantState, ability: AbilityName) -> int:
    """Return the live score, never mutating the source card."""
    if ability not in ABILITIES:
        raise ValueError(f"Unknown ability: {ability}")
    scores = state.template.ability_scores
    if scores is None:
        raise ValueError("Ability score reduction requires certified ability scores.")
    reduction = state.ability_score_reductions.get(ability, 0)
    if type(reduction) is not int or reduction < 0:
        raise ValueError("Invalid ability score reduction state.")
    return max(0, scores.score(ability) - reduction)


def effective_ability_modifier(state: CombatantState, ability: AbilityName) -> int:
    return (effective_ability_score(state, ability) - 10) // 2


def apply_ability_score_reduction(
    state: CombatantState,
    ability: AbilityName,
    amount: int,
    *,
    zero_kills: bool = False,
    affected_states: list[CombatantState] | None = None,
) -> AbilityScoreReductionResult:
    """Apply source-declared score drain, optionally killing at zero.

    An effect that cannot kill must leave the target at least one point;
    explicit zero_kills uses existing instant-death prevention/lifecycle.
    Repeated hits stack in fight state. Greater Restoration already removes
    one named ability's reduction via the shared restoration resolver.
    """
    if type(amount) is not int or amount < 0:
        raise ValueError("Ability score reduction amount must be a nonnegative integer.")
    before = effective_ability_score(state, ability)
    if state.is_dead or amount == 0 or before == 0:
        return AbilityScoreReductionResult(ability, before, before, 0)
    minimum = 0 if zero_kills else 1
    after = max(minimum, before - amount)
    applied = before - after
    if applied:
        state.ability_score_reductions[ability] = (
            state.ability_score_reductions.get(ability, 0) + applied
        )
    outcome = apply_instant_death(state, affected_states=affected_states) if (
        zero_kills and after == 0 and applied
    ) else None
    return AbilityScoreReductionResult(ability, before, after, applied, outcome)
