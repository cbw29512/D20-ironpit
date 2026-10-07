from __future__ import annotations

from app.domain.actions import ConditionRemovalAction


WAKE_SLEEPER_ACTION = ConditionRemovalAction(
    id="wake-sleeper",
    name="Wake Sleeper",
    action_cost="action",
    range_ft=5,
    target_mode="ally",
    removable_conditions=["unconscious"],
    max_conditions_per_use=1,
    requires_explicit_effect_permission=True,
    animation="condition-removal",
)
