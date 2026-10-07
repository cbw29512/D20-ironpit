from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def _damage_type_key(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _add_typed_damage(state: CombatantState, damage_type, amount: int) -> None:
    key = _damage_type_key(damage_type)
    state.damage_taken_this_turn_by_type[key] = state.damage_taken_this_turn_by_type.get(key, 0) + amount


def note_turn_damage(
    state: CombatantState,
    amount: int,
    damage_types: set,
    damage_components=None,
) -> None:
    """Accumulate applied damage by type for source-owned during-turn triggers."""
    try:
        if amount <= 0:
            return
        remaining = amount
        for component in list(damage_components or []):
            applied = max(0, int(component.applied_total or 0))
            credited = min(applied, remaining)
            if credited:
                _add_typed_damage(state, component.damage_type, credited)
                remaining -= credited
            if remaining <= 0:
                return
        if remaining > 0 and len(damage_types) == 1:
            _add_typed_damage(state, next(iter(damage_types)), remaining)
    except Exception:
        logger.exception("Failed to record per-turn typed damage for %s.", state.template.name)
        raise


def note_single_type_turn_damage(
    state: CombatantState,
    amount: int,
    damage_types: set,
) -> None:
    """Compatibility wrapper for callers that only know a single damage type."""
    note_turn_damage(state, amount, damage_types)


def clear_turn_damage(setup: EncounterSetup) -> None:
    """Clear damage accumulated during the just-ended active turn."""
    try:
        for member in [*setup.heroes, *setup.monsters]:
            member.state.damage_taken_this_turn_by_type = {}
    except Exception:
        logger.exception("Failed to clear per-turn typed damage state.")
        raise


def note_turn_damage_and_trigger(
    state: CombatantState,
    amount: int,
    damage_types: set,
    damage_components=None,
) -> None:
    """Record applied typed damage, then dispatch source-owned damage triggers."""
    try:
        before = dict(state.damage_taken_this_turn_by_type)
        note_turn_damage(state, amount, damage_types, damage_components)
        from app.combat.damage_taken_effects import apply_damage_taken_timed_effects
        apply_damage_taken_timed_effects(state, before)
    except Exception:
        logger.exception("Failed to dispatch typed-damage triggers for %s.", state.template.name)
        raise
