from __future__ import annotations

import logging

from app.combat.modifier_stack import effective_speed
from app.domain.movement import MovementModes
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def effective_movement_modes(state: CombatantState) -> MovementModes:
    """Return printed movement modes plus source-owned active grants."""
    try:
        modes = state.template.movement_modes.model_copy(deep=True)
        for effect in state.timed_effects:
            for grant in effect.owned_movement_mode_grants:
                speed = effective_speed(state) if grant.match_current_speed else grant.fixed_speed_ft
                if speed is None:
                    raise ValueError(f"Movement grant {grant.mode} has no resolved speed.")
                field = f"{grant.mode}_ft"
                setattr(modes, field, max(getattr(modes, field), speed))
        return modes
    except Exception as exc:
        logger.exception("Failed to resolve effective movement modes for %s.", state.template.name)
        raise RuntimeError("Effective movement modes could not be resolved.") from exc
