from __future__ import annotations

from app.domain.effect_removal import EffectRemovalAction
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

_SOURCE = "D&D SRD 5.1 (2014): Paladin spells and class features"


def cleansing_touch_2014() -> EffectRemovalAction:
    return EffectRemovalAction(
        id="cleansing-touch",
        name="Cleansing Touch",
        level=0,
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


def divine_favor_2014() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="divine-favor",
        name="Divine Favor",
        level=1,
        action_cost="bonus_action",
        range_ft=0,
        duration_minutes=1,
        target_policy="self",
        concentration=True,
        priority=25,
        modifier_effects=[
            SpellModifierEffect(
                kind="bonus-damage",
                dice_count=1,
                dice_size=4,
                damage_type="radiant",
            ),
        ],
        animation="divine-favor",
        source=_SOURCE,
    )
