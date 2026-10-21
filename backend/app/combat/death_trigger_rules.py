"""Shared death-trigger eligibility; card-bound effect execution is separate.

No death-trigger action fires on a character's initial drop to zero HP.
The caller owns event resolution and must consume the trigger exactly once.
"""
from __future__ import annotations

from app.domain.models import CombatantState

DEATH_TRIGGER_BUFF = "death-trigger"


def death_trigger_ready(state: CombatantState) -> bool:
    """A fight-local Death Trigger buff fires only when this creature is dead."""
    return (
        DEATH_TRIGGER_BUFF in state.active_buff_effect_ids
        and state.is_dead
        and not state.feature_use_counts.get(DEATH_TRIGGER_BUFF, 0)
    )


def consume_death_trigger(state: CombatantState) -> bool:
    """Reserve a ready death event once; the effect resolver handles its payload."""
    if not death_trigger_ready(state):
        return False
    state.feature_use_counts[DEATH_TRIGGER_BUFF] = 1
    return True
