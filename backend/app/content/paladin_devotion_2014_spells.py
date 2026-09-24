from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.cleric_life_domain import AID
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.content.shared_spells_2014 import beacon_of_hope_2014, lesser_restoration_2014, sanctuary_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.domain.actions import ConditionRemovalAction, HealingAction, SaveDamageComponent
from app.domain.effect_removal import EffectRemovalAction
from app.domain.persistent_hazards import PersistentHazardAction
from app.domain.progression import PassiveModifierGrant
from app.domain.size import CreatureSize
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect, SpellSaveAction

_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]
_SOURCE = "D&D SRD 5.1 (2014): Paladin and Oath of Devotion spells"
logger = logging.getLogger(__name__)


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
            SpellModifierEffect(
                kind="effect-immunity", effect_tag="possession",
                source_creature_types=_PROTECTED_TYPES,
            ),
        ],
        animation="protection", source=_SOURCE,
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
    if level >= 13:
        actions.append(freedom_of_movement_2014())
    return actions



def freedom_of_movement_2014() -> DefensiveSpellAction:
    """Compile Freedom of Movement from universal source-owned movement defenses."""
    try:
        return DefensiveSpellAction(
            id="freedom-of-movement",
            name="Freedom of Movement",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            owned_magical_condition_immunities=["paralyzed", "restrained"],
            difficult_terrain_bypass_scope="all",
            prevents_magical_speed_reduction=True,
            nonmagical_grapple_escape_movement_cost_ft=5,
            concentration=False,
            priority=46,
            animation="freedom-of-movement",
            source=_SOURCE,
        )
    except Exception:
        logger.exception("Failed to build 2014 Freedom of Movement.")
        raise

def guardian_of_faith_2014(save_dc: int) -> PersistentHazardAction:
    """Bind Guardian of Faith to the shared stationary persistent-hazard schema."""
    try:
        return PersistentHazardAction(
            id="guardian-of-faith",
            name="Guardian of Faith",
            level=4,
            action_cost="action",
            cast_range_ft=30,
            duration_rounds=4800,
            footprint_size=CreatureSize.LARGE,
            trigger_radius_ft=10,
            save_ability="dexterity",
            dc=save_dc,
            failure_damage=20,
            success_damage=10,
            damage_type="radiant",
            max_total_damage=60,
            animation="guardian-of-faith",
            source=_SOURCE,
        )
    except Exception:
        logger.exception("Failed to build 2014 Guardian of Faith at save DC %s", save_dc)
        raise


def build_paladin_persistent_hazard_actions_2014(
    level: int,
    charisma_modifier: int,
) -> list[PersistentHazardAction]:
    """Compile currently supported persistent-hazard oath spells for Aurelia."""
    try:
        if level < 13:
            return []
        save_dc = 8 + proficiency_bonus(level) + charisma_modifier
        return [guardian_of_faith_2014(save_dc)]
    except Exception:
        logger.exception("Failed to compile 2014 Paladin persistent hazards at level %s", level)
        raise


def cleansing_touch_2014() -> EffectRemovalAction:
    """Bind Cleansing Touch to generic tracked-spell removal with no ability check."""
    return EffectRemovalAction(
        id="cleansing-touch",
        name="Cleansing Touch",
        level=9,
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


def purity_of_spirit_2014() -> PassiveModifierGrant:
    """Reuse Protection from Evil and Good modifier semantics as a passive feature."""
    try:
        protection = protection_from_evil_and_good_2014()
        return PassiveModifierGrant(
            source_id="purity-of-spirit",
            source_name="Purity of Spirit",
            modifier_effects=[effect.model_copy(deep=True) for effect in protection.modifier_effects],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Purity of Spirit passive modifiers")
        raise


def flame_strike_2014(save_dc: int) -> SpellSaveAction:
    """Bind Flame Strike to the generic split-damage save spell schema."""
    try:
        return SpellSaveAction(
            id="flame-strike",
            name="Flame Strike",
            level=5,
            action_cost="action",
            range_ft=60,
            area_radius_ft=10,
            save_ability="dexterity",
            dc=save_dc,
            damage_components=[
                SaveDamageComponent(
                    source="Flame Strike (Fire)",
                    dice_count=4,
                    dice_size=6,
                    damage_type="fire",
                ),
                SaveDamageComponent(
                    source="Flame Strike (Radiant)",
                    dice_count=4,
                    dice_size=6,
                    damage_type="radiant",
                ),
            ],
            success_damage="half",
            animation="flame-strike",
        )
    except Exception:
        logger.exception("Failed to build 2014 Flame Strike at save DC %s", save_dc)
        raise


def build_paladin_spell_save_actions_2014(
    level: int,
    charisma_modifier: int,
) -> list[SpellSaveAction]:
    """Compile currently supported Devotion save-based oath spells."""
    try:
        if level < 17:
            return []
        return [flame_strike_2014(8 + proficiency_bonus(level) + charisma_modifier)]
    except Exception:
        logger.exception("Failed to compile 2014 Paladin save spells at level %s", level)
        raise
