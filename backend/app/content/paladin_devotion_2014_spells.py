from __future__ import annotations

from app.content.character_math import proficiency_bonus
from app.content.cleric_life_domain import AID
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.actions import ConditionRemovalAction, HealingAction
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


def build_paladin_healing_actions_2014(level: int, charisma_modifier: int) -> list[HealingAction]:
    actions = [HealingAction(
        id="lay-on-hands-heal", name="Lay on Hands", action_cost="action", range_ft=5,
        target_mode="self_or_ally", dice_count=0, healing_bonus=5 * level,
        resource_id="lay-on-hands", resource_cost=5 * level, animation="healing",
    )]
    if level >= 2:
        actions.append(HealingAction(
            id="cure-wounds", name="Cure Wounds", action_cost="action", range_ft=5,
            target_mode="self_or_ally", dice_count=1, dice_size=8, healing_bonus=charisma_modifier,
            resource_id="spell-slot-1", resource_cost=1, animation="healing",
        ))
    return actions


def build_paladin_condition_removal_actions_2014(level: int) -> list[ConditionRemovalAction]:
    actions = [ConditionRemovalAction(
        id="lay-on-hands-poison", name="Lay on Hands", action_cost="action", range_ft=5,
        target_mode="self_or_ally", removable_conditions=["poisoned"], max_conditions_per_use=1,
        resource_costs_per_condition={"lay-on-hands": 5}, animation="condition-removal",
    )]
    if level >= 5:
        actions.append(lesser_restoration_2014())
    return actions


def build_paladin_defensive_spells_2014(level: int, charisma_modifier: int) -> list[DefensiveSpellAction]:
    if level < 2:
        return []
    source = "D&D SRD 5.1 (2014): Paladin spell list"
    actions = [
        BLESS.model_copy(update={"source": source}),
        SHIELD_OF_FAITH.model_copy(update={"source": source}),
    ]
    if level >= 3:
        actions.extend([
            protection_from_evil_and_good_2014(),
            sanctuary_2014(8 + proficiency_bonus(level) + charisma_modifier),
        ])
    if level >= 9:
        actions.append(beacon_of_hope_2014())
    if level >= 10:
        actions.append(AID.model_copy(update={"source": source}))
    return actions
