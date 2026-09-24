from __future__ import annotations

from app.domain.effect_removal import EffectRemovalAction


def cleansing_touch_2014() -> EffectRemovalAction:
    """2014 Paladin Cleansing Touch expressed through generic spell-effect removal."""
    return EffectRemovalAction(
        id="cleansing-touch",
        name="Cleansing Touch",
        level=1,
        action_cost="action",
        range_ft=5,
        casting_ability="charisma",
        target_mode="self_or_ally",
        auto_remove_max_level=9,
        resource_id="cleansing-touch",
        resource_cost=1,
        expends_spell_slot=False,
        animation="cleansing-touch",
    )
