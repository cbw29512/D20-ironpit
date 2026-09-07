from __future__ import annotations

from app.domain.models import CombatantState

_FEATURE_ID = "boon-combat-prowess"


def apply_combat_prowess(state: CombatantState, hit: bool, turn_key: str) -> bool:
    """Turn one missed attack roll into a hit, refreshing at the start of the next turn."""
    if hit or not state.template.progression_features.combat_prowess:
        return hit
    if state.feature_last_turn_keys.get(_FEATURE_ID) == turn_key:
        return hit
    state.feature_last_turn_keys[_FEATURE_ID] = turn_key
    return True
