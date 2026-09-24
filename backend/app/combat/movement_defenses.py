from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def ignores_difficult_terrain(state: CombatantState, *, magical: bool) -> bool:
    """Return whether active source-owned defenses ignore this difficult-terrain source."""
    try:
        scopes = [
            grant.scope
            for grant in state.template.progression_features.difficult_terrain_bypass_grants
        ]
        scopes.extend(
            effect.difficult_terrain_bypass_scope
            for effect in state.timed_effects
            if effect.difficult_terrain_bypass_scope is not None
        )
        return any(scope == "all" or (scope == "nonmagical" and not magical) for scope in scopes)
    except Exception as exc:
        logger.exception(
            "Failed to resolve difficult-terrain bypass for %s.",
            state.template.name,
        )
        raise RuntimeError("Difficult-terrain bypass could not be resolved.") from exc


def prevents_magical_speed_reduction(state: CombatantState) -> bool:
    """Return whether a source-owned active effect blocks magical Speed reduction."""
    try:
        return any(effect.prevents_magical_speed_reduction for effect in state.timed_effects)
    except Exception as exc:
        logger.exception("Failed to resolve magical Speed protection for %s.", state.template.name)
        raise RuntimeError("Magical Speed protection could not be resolved.") from exc


def nonmagical_grapple_escape_cost_ft(state: CombatantState) -> int | None:
    """Return the cheapest active movement cost that automatically escapes a nonmagical grapple."""
    try:
        costs = [
            effect.nonmagical_grapple_escape_movement_cost_ft
            for effect in state.timed_effects
            if effect.nonmagical_grapple_escape_movement_cost_ft > 0
        ]
        return min(costs) if costs else None
    except Exception as exc:
        logger.exception("Failed to resolve movement-based grapple escape for %s.", state.template.name)
        raise RuntimeError("Movement-based grapple escape could not be resolved.") from exc
