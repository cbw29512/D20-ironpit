from __future__ import annotations

from app.domain.actions import ConditionRemovalAction
from app.domain.effect_removal import EffectRemovalAction
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]
_SOURCE = "D&D SRD 5.1 (2014): Paladin and Oath of Devotion spells"


def protection_from_evil_and_good_2014() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="protection-from-evil-and-good", name="Protection from Evil and Good",
        level=1, action_cost="action", range_ft=5, duration_minutes=10,
        target_policy="friendly", target_count=1, concentration=True, priority=38,
        modifier_effects=[
            SpellModifierEffect(
                kind="attacks-against-disadvantage",
                source_creature_types=_PROTECTED_TYPES,
            ),
            SpellModifierEffect(
                kind="condition-immunity", condition_id="charmed",
                source_creature_types=_PROTECTED_TYPES,
            ),
            SpellModifierEffect(
                kind="condition-immunity", condition_id="frightened",
                source_creature_types=_PROTECTED_TYPES,
            ),
        ],
        animation="protection", source=_SOURCE,
    )


def sanctuary_2014(save_dc: int) -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="sanctuary", name="Sanctuary", level=1, action_cost="bonus_action",
        range_ft=30, duration_minutes=1, target_policy="friendly", target_count=1,
        priority=32,
        modifier_effects=[
            SpellModifierEffect(
                kind="targeting-save-gate", save_ability="wisdom", save_dc=save_dc,
                ends_on_owner_attack=True,
            ),
        ],
        animation="sanctuary", source=_SOURCE,
    )


def lesser_restoration_2014() -> ConditionRemovalAction:
    return ConditionRemovalAction(
        id="lesser-restoration", name="Lesser Restoration", action_cost="action",
        range_ft=5, target_mode="self_or_ally",
        removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
        max_conditions_per_use=1, resource_costs={"spell-slot-2": 1},
        expends_spell_slot=True, animation="lesser-restoration",
    )


def beacon_of_hope_2014() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="beacon-of-hope", name="Beacon of Hope", level=3, action_cost="action",
        range_ft=30, duration_minutes=1, target_policy="friendly", target_count=20,
        concentration=True, priority=60,
        modifier_effects=[
            SpellModifierEffect(kind="saving-throw-advantage", save_ability="wisdom"),
            SpellModifierEffect(kind="death-save-advantage"),
            SpellModifierEffect(kind="healing-maximize"),
        ],
        animation="beacon-of-hope", source=_SOURCE,
    )


def dispel_magic_2014() -> EffectRemovalAction:
    return EffectRemovalAction(
        id="dispel-magic", name="Dispel Magic", level=3, action_cost="action",
        range_ft=120, casting_ability="charisma", target_mode="enemy",
        auto_remove_max_level=3, resource_id="spell-slot-3", resource_cost=1,
        expends_spell_slot=True, animation="dispel-magic",
    )
