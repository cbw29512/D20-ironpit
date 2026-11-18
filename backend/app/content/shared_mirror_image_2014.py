from __future__ import annotations

from app.domain.timed_self_buffs import IllusoryDuplicateDefense, TimedSelfBuffAction


def mirror_image_2014(resource_id: str | None) -> TimedSelfBuffAction:
    """Return the shared 2014 Mirror Image action with printed spell parameters."""
    return TimedSelfBuffAction(
        id="mirror-image",
        name="Mirror Image",
        action_cost="action",
        resource_id=resource_id,
        resource_cost=1,
        duration_rounds=10,
        expiry_timing="source_turn_start",
        magical_effect=True,
        illusory_duplicate_defense=IllusoryDuplicateDefense(),
        priority=85,
        animation="mirror-image",
    )
