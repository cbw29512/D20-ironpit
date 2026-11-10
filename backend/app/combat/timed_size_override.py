"""Fight-local source-owned size override, independent of monster identity."""
from __future__ import annotations

import logging

from app.domain.models import CombatantState, TimedEffect
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def apply_size_override(
    state: CombatantState, source_id: str, action_id: str, size: CreatureSize,
) -> None:
    """The immutable card remains intact; only this fight's template changes."""
    try:
        if state.replacement_form is not None:
            raise ValueError("Size override cannot overlap a replacement form.")
        if any(effect.owned_override_size is not None for effect in state.timed_effects):
            raise ValueError("A fight-local size override is already active.")
        match = [
            effect for effect in state.timed_effects
            if effect.source_id == source_id and effect.source_effect_id == action_id
        ]
        if len(match) != 1:
            raise ValueError("Size change must own one active timed-effect group.")
        if state.template.size == size:
            raise ValueError("Size override requires a genuine size change.")
        effect = match[0]
        effect.owned_previous_size = state.template.size
        effect.owned_override_size = size
        state.template = state.template.model_copy(update={"size": size})
    except Exception:
        logger.exception("Could not apply temporary size %s for %s.", size, state.template.id)
        raise


def restore_size_override(state: CombatantState, effect: TimedEffect) -> None:
    """Owner-targeted removal (expiry/dispel) restores the former size."""
    try:
        previous, current = effect.owned_previous_size, effect.owned_override_size
        if current is None:
            return
        if previous is None or state.template.size != current:
            raise ValueError("Temporary size state drifted before source effect removal.")
        state.template = state.template.model_copy(update={"size": previous})
    except Exception:
        logger.exception("Could not restore source-owned size for %s.", state.template.id)
        raise
