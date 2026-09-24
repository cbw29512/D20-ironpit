from __future__ import annotations

from app.domain.effect_removal import EffectRemovalAction
from app.domain.passive_modifiers import PassiveModifierGrant

_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]


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


def purity_of_spirit_2014() -> list[PassiveModifierGrant]:
    """Always-on Protection from Evil and Good defenses for Devotion Paladin 15."""
    return [
        PassiveModifierGrant(
            source_id="purity-of-spirit",
            source_name="Purity of Spirit",
            kind="attacks-against-disadvantage",
            source_creature_types=_PROTECTED_TYPES,
        ),
        PassiveModifierGrant(
            source_id="purity-of-spirit",
            source_name="Purity of Spirit",
            kind="condition-immunity",
            condition_id="charmed",
            source_creature_types=_PROTECTED_TYPES,
        ),
        PassiveModifierGrant(
            source_id="purity-of-spirit",
            source_name="Purity of Spirit",
            kind="condition-immunity",
            condition_id="frightened",
            source_creature_types=_PROTECTED_TYPES,
        ),
    ]
