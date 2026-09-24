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
