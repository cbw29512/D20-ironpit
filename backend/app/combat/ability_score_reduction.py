"""Source-neutral fight-state ability-score reductions.

An immutable combatant card holds the base score. The existing fight-state
ability_score_reductions mapping holds cumulative reductions only for the current fight.
This is an effect primitive, not a monster-specific attack resolver.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.instant_death import apply_terminal_death
from app.domain.character_builds import AbilityName
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)

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


def ability_modifier_delta(state: CombatantState, ability: AbilityName | None) -> int:
    """Apply live score loss to source-final bonuses without rebuilding the card."""
    if ability is None or not state.ability_score_reductions.get(ability, 0):
        return 0
    if state.template.ability_scores is None:
        raise ValueError("Drained attack/check requires a certified source ability score.")
    return effective_ability_modifier(state, ability) - state.template.ability_scores.modifier(ability)


def apply_ability_score_reduction(
    state: CombatantState,
    ability: AbilityName,
    amount: int,
    *,
    zero_kills: bool = False,
    affected_states: list[CombatantState] | None = None,
) -> AbilityScoreReductionResult:
    """Apply a cumulative fight-only score reduction and kill at zero.

    All six ability scores share the same 0-score terminal death rule in Iron
    Pit. The legacy zero_kills argument is accepted only for old call sites;
    it can never make a score-0 result nonlethal. Source templates are not
    mutated and new combat state starts with the original scores.
    """
    try:
        if type(amount) is not int or amount < 0:
            raise ValueError("Ability score reduction amount must be a nonnegative integer.")
        before = effective_ability_score(state, ability)
        if state.is_dead or amount == 0 or before == 0:
            return AbilityScoreReductionResult(ability, before, before, 0)
        after = max(0, before - amount)
        applied = before - after
        if applied:
            state.ability_score_reductions[ability] = (
                state.ability_score_reductions.get(ability, 0) + applied
            )
        outcome = apply_terminal_death(state, affected_states=affected_states) if (
            after == 0 and applied
        ) else None
        return AbilityScoreReductionResult(ability, before, after, applied, outcome)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ability-score reduction failed for %s (%s).", state.template.name, ability)
        raise RuntimeError("Ability-score reduction could not be resolved.") from exc
