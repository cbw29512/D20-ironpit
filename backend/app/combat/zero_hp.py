from __future__ import annotations

import logging
from typing import Literal

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
ZeroHpOutcome = Literal["damaged", "unconscious", "dead", "unchanged"]


def reset_death_saves(state: CombatantState) -> None:
    state.death_save_successes = 0
    state.death_save_failures = 0


def _mark_dead(state: CombatantState) -> ZeroHpOutcome:
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    return "dead"


def restore_hit_points(state: CombatantState, amount: int) -> int:
    """Restore true HP; ordinary healing cannot restore a dead creature."""
    if amount < 0:
        raise ValueError("Healing cannot be negative.")
    if state.is_dead or amount == 0:
        return 0
    before = state.current_hp
    state.current_hp = min(state.template.max_hp, before + amount)
    healed = state.current_hp - before
    if healed > 0:
        state.is_alive = True
        state.is_unconscious = False
        state.is_stable = False
        reset_death_saves(state)
    return healed


def apply_damage(state: CombatantState, amount: int, *, critical: bool = False) -> ZeroHpOutcome:
    """Apply SRD 5.2.1 zero-HP rules for ordinary monsters and player characters."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if amount == 0 or state.is_dead:
            return "unchanged"

        if state.current_hp > 0:
            hp_before = state.current_hp
            state.current_hp = max(0, hp_before - amount)
            if state.current_hp > 0:
                return "damaged"
            if state.template.kind == "monster":
                return _mark_dead(state)

            remaining_damage = max(0, amount - hp_before)
            if remaining_damage >= state.template.max_hp:
                return _mark_dead(state)
            state.is_alive = True
            state.is_unconscious = True
            state.is_stable = False
            return "unconscious"

        if state.template.kind == "monster":
            return _mark_dead(state)
        if amount >= state.template.max_hp:
            return _mark_dead(state)

        state.is_stable = False
        state.is_unconscious = True
        state.death_save_failures = min(
            3,
            state.death_save_failures + (2 if critical else 1),
        )
        if state.death_save_failures >= 3:
            return _mark_dead(state)
        return "unconscious"
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Zero-HP damage resolution failed for %s.", state.template.name)
        raise RuntimeError("Zero-HP damage could not be resolved.") from exc
