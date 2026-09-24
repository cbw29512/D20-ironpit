from __future__ import annotations

from app.domain.effect_removal import EffectRemovalAction


def cleansing_touch_2014() -> EffectRemovalAction:
    return EffectRemovalAction(
        id="cleansing-touch",
        name="Cleansing Touch",
        level=0,
        action_cost="action",
        range_ft=5,
        target_mode="self_or_ally",
        auto_remove_max_level=9,
        resource_id="cleansing-touch",
        resource_cost=1,
        expends_spell_slot=False,
        animation="cleansing-touch",
    )


def dispel_magic_2014() -> EffectRemovalAction:
    return EffectRemovalAction(
        id="dispel-magic",
        name="Dispel Magic",
        level=3,
        action_cost="action",
        range_ft=120,
        casting_ability="charisma",
        target_mode="enemy",
        auto_remove_max_level=3,
        resource_id="spell-slot-3",
        resource_cost=1,
        expends_spell_slot=True,
        animation="dispel-magic",
    )
