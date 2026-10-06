from __future__ import annotations

import logging

from app.combat.exhaustion import reduce_exhaustion
from app.combat.hit_points import effective_max_hp
from app.domain.actions import ConditionRemovalAction
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def apply_restoration_riders(
    target: EncounterCombatant,
    action: ConditionRemovalAction,
    selected: list[str] | None = None,
) -> list[str]:
    """Apply only the selected Greater Restoration-style riders."""
    try:
        wanted = set(selected or [])
        applied: list[str] = []
        if (
            "exhaustion" in wanted
            and action.reduces_exhaustion_levels
            and target.state.exhaustion_level
        ):
            reduce_exhaustion(target.state, action.reduces_exhaustion_levels)
            applied.append("exhaustion")
        if "curse" in wanted and target.state.active_curses and (
            action.removes_curses or action.removes_all_curses
        ):
            if action.removes_all_curses:
                target.state.active_curses = []
            else:
                target.state.active_curses = target.state.active_curses[1:]
            applied.append("curse")
        if (
            "ability-score-reduction" in wanted
            and action.removes_ability_score_reductions
            and target.state.ability_score_reductions
        ):
            ability = sorted(target.state.ability_score_reductions)[0]
            target.state.ability_score_reductions = {
                key: value
                for key, value in target.state.ability_score_reductions.items()
                if key != ability
            }
            applied.append("ability-score-reduction")
        if (
            "hit-point-maximum-reduction" in wanted
            and action.removes_hit_point_maximum_reductions
            and target.state.hit_point_maximum_reduction
        ):
            target.state.hit_point_maximum_reduction = 0
            target.state.current_hp = min(target.state.current_hp, effective_max_hp(target.state))
            applied.append("hit-point-maximum-reduction")
        return applied
    except Exception:
        logger.exception("Failed to apply restoration riders from %s.", action.id)
        raise


def apply_hit_point_maximum_reduction_state(
    state,
    amount: int,
    *,
    zero_max_hp_kills: bool = False,
) -> int:
    """Apply a generic hit-point maximum reduction to one combatant state."""
    try:
        if amount < 0:
            raise ValueError("Hit point maximum reduction cannot be negative.")
        if amount == 0:
            return 0
        if any(effect.prevent_hit_point_maximum_reduction for effect in state.timed_effects):
            return 0
        state.hit_point_maximum_reduction += amount
        raw_maximum = state.template.max_hp + state.max_hp_bonus - state.hit_point_maximum_reduction
        if zero_max_hp_kills and raw_maximum <= 0:
            state.current_hp = 0
            state.is_alive = False
            state.is_dead = True
            state.is_unconscious = False
            state.is_stable = False
            state.death_save_successes = 0
            state.death_save_failures = 0
            return amount
        maximum = effective_max_hp(state)
        if state.current_hp > maximum:
            state.current_hp = maximum
        return amount
    except Exception:
        logger.exception("Failed to reduce hit point maximum for %s.", state.template.name)
        raise


def apply_hit_point_maximum_reduction(target: EncounterCombatant, amount: int) -> int:
    try:
        return apply_hit_point_maximum_reduction_state(target.state, amount)
    except Exception:
        logger.exception("Failed to reduce hit point maximum for %s.", target.combatant_id)
        raise
