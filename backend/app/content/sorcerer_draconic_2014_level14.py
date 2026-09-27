from __future__ import annotations

from app.domain.movement import MovementModeGrant
from app.domain.timed_self_buffs import TimedSelfBuffAction


def dragon_wings_2014() -> TimedSelfBuffAction:
    """2014 Dragon Wings as a persistent bonus-action movement-mode grant."""
    return TimedSelfBuffAction(
        id="dragon-wings",
        name="Dragon Wings",
        action_cost="bonus_action",
        duration_rounds=None,
        movement_mode_grants=[
            MovementModeGrant(mode="fly", match_current_speed=True),
        ],
        expiry_timing=None,
        priority=80,
        animation="dragon-wings",
    )
