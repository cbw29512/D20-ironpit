from __future__ import annotations

from app.domain.models import CombatantState

GRAPPLED_EFFECT_ID = "grappled"
RESTRAINED_EFFECT_ID = "restrained"


def sync_grapple_effect_ids(state: CombatantState) -> None:
    if state.grapple_sources:
        if GRAPPLED_EFFECT_ID not in state.active_effect_ids:
            state.active_effect_ids.append(GRAPPLED_EFFECT_ID)
        if "dodge" in state.active_effect_ids:
            state.active_effect_ids.remove("dodge")
    elif GRAPPLED_EFFECT_ID in state.active_effect_ids:
        state.active_effect_ids.remove(GRAPPLED_EFFECT_ID)
    restrained = any(source.restrains for source in state.grapple_sources)
    if restrained and RESTRAINED_EFFECT_ID not in state.active_effect_ids:
        state.active_effect_ids.append(RESTRAINED_EFFECT_ID)
    elif not restrained and RESTRAINED_EFFECT_ID in state.active_effect_ids:
        state.active_effect_ids.remove(RESTRAINED_EFFECT_ID)
    linked = {item for source in state.grapple_sources for item in source.linked_conditions}
    for condition in linked:
        if condition not in state.active_effect_ids:
            state.active_effect_ids.append(condition)


def drop_orphaned_linked_conditions(state: CombatantState, removed: set[str]) -> None:
    remaining = {item for source in state.grapple_sources for item in source.linked_conditions}
    timed = {effect.effect_id for effect in state.timed_effects}
    for condition in removed - remaining - timed:
        if condition in state.active_effect_ids:
            state.active_effect_ids.remove(condition)
