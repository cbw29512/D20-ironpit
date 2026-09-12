from __future__ import annotations

from app.domain.actions import ConditionRemovalAction

WAKE_SLEEPER_ID = "wake-sleeper"


def wake_sleeper_action() -> ConditionRemovalAction:
    """Universal basic Action for source effects that explicitly allow an adjacent creature to wake a target."""
    return ConditionRemovalAction(
        id=WAKE_SLEEPER_ID,
        name="Wake Sleeper",
        action_cost="action",
        range_ft=5,
        target_mode="ally",
        removable_conditions=["unconscious"],
        max_conditions_per_use=1,
        animation="condition-removal",
    )


__all__ = ["WAKE_SLEEPER_ID", "wake_sleeper_action"]
