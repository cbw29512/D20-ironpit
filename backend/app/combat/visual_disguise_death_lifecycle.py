"""Card-defined visual illusion expiry at the owner's actual death.

The original card is immutable. Death detection and state mutation are
universal; no monster/ability name is consulted.
"""
from __future__ import annotations

from app.domain.models import CombatantState


def end_visual_disguise_if_dead(state: CombatantState) -> bool:
    rule = state.template.visual_disguise_action
    if (not state.is_dead or rule is None or not rule.ends_if_owner_dead
            or not state.magical_visual_disguise_active):
        return False
    state.magical_visual_disguise_active = False
    return True
