from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.orc import use_relentless_endurance
from app.combat.regeneration import regeneration_defers_death
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)
PRONE_EFFECT_ID = "prone"


def _finish_zero_hp(
    state: CombatantState,
    affected_states: list[CombatantState] | None,
) -> None:
    try:
        if use_relentless_endurance(state, 0):
            return
        if state.template.kind == "monster":
            if regeneration_defers_death(state):
                state.is_alive = True
                state.is_dead = False
                return
            state.is_alive = False
            state.is_dead = True
            state.is_unconscious = False
            state.is_stable = False
        else:
            state.is_alive = True
            state.is_dead = False
            state.is_unconscious = True
            state.is_stable = False
            if (
                not condition_is_immune(state, PRONE_EFFECT_ID)
                and PRONE_EFFECT_ID not in state.active_effect_ids
            ):
                state.active_effect_ids.append(PRONE_EFFECT_ID)
        state.active_effect_ids = [
            effect for effect in state.active_effect_ids if effect != "dodge"
        ]
        from app.combat.concentration import end_concentration_if_incapacitated
        end_concentration_if_incapacitated(state, affected_states)
    except Exception as exc:
        logger.exception("Failed zero-HP transition after direct HP loss for %s.", state.template.name)
        raise RuntimeError("Direct HP-loss zero-HP transition failed.") from exc


def lose_hit_points(
    state: CombatantState,
    amount: int,
    *,
    affected_states: list[CombatantState] | None = None,
) -> int:
    """Lose true HP without damage, Temporary HP, defenses, or damage triggers."""
    try:
        if amount < 0:
            raise ValueError("Hit Point loss cannot be negative.")
        if amount == 0 or state.is_dead or state.current_hp == 0:
            return 0
        before = state.current_hp
        state.current_hp = max(0, before - amount)
        lost = before - state.current_hp
        if state.current_hp == 0:
            _finish_zero_hp(state, affected_states)
        return lost
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Direct Hit Point loss failed for %s.", state.template.name)
        raise RuntimeError("Hit Point loss could not be resolved.") from exc
