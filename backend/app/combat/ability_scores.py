from __future__ import annotations

import logging

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.dice import DiceProvider
from app.domain.ability_reduction import AbilityScoreReductionOnHit
from app.domain.actions import AbilityName
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def base_ability_score(state: CombatantState, ability: AbilityName) -> int:
    scores = state.template.ability_scores
    if scores is None:
        raise ValueError(f"{state.template.name} lacks certified ability scores.")
    return scores.score(ability)


def effective_ability_score(state: CombatantState, ability: AbilityName) -> int:
    base = base_ability_score(state, ability)
    return max(0, base - state.ability_score_reductions.get(ability, 0))


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def ability_modifier_delta(state: CombatantState, ability: AbilityName) -> int:
    return ability_modifier(effective_ability_score(state, ability)) - ability_modifier(base_ability_score(state, ability))


def _kill_from_reduction(state: CombatantState, affected_states: list[CombatantState] | None) -> None:
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != "dodge"]
    end_concentration_if_incapacitated(state, affected_states)


def apply_ability_score_reduction(
    state: CombatantState,
    effect: AbilityScoreReductionOnHit,
    dice: DiceProvider,
    affected_states: list[CombatantState] | None = None,
) -> tuple[int, int, int]:
    """Apply a cumulative score reduction and return (before, reduction, after)."""
    try:
        before = effective_ability_score(state, effect.ability)
        rolled = sum(dice.roll(effect.dice_size) for _ in range(effect.dice_count))
        after = max(effect.minimum_score, before - rolled)
        applied = before - after
        if applied:
            state.ability_score_reductions[effect.ability] = state.ability_score_reductions.get(effect.ability, 0) + applied
        if effect.dies_at_minimum and after <= effect.minimum_score and not state.is_dead:
            _kill_from_reduction(state, affected_states)
        return before, applied, after
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ability-score reduction failed for %s.", state.template.name)
        raise RuntimeError("Ability-score reduction could not be resolved.") from exc
