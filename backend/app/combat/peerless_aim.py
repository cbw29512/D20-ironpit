from __future__ import annotations

from app.domain.models import CombatantState

PEERLESS_AIM_USE_KEY = "peerless-aim-used"


def refresh_peerless_aim(state: CombatantState) -> None:
    state.feature_last_turn_keys.pop(PEERLESS_AIM_USE_KEY, None)


def resolve_peerless_aim_miss(state: CombatantState, hit: bool) -> tuple[bool, bool]:
    """Turn one missed attack roll into a hit until the user's next turn starts."""
    if hit or not state.template.progression_features.peerless_aim:
        return hit, False
    if PEERLESS_AIM_USE_KEY in state.feature_last_turn_keys:
        return hit, False
    state.feature_last_turn_keys[PEERLESS_AIM_USE_KEY] = "used"
    return True, True
