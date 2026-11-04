from __future__ import annotations

import logging

from app.domain.actions import ConditionRemovalAction
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014"


def sanctuary_2014(save_dc: int) -> DefensiveSpellAction:
    """Build shared 2014 Sanctuary through the universal targeting-save gate."""
    try:
        return DefensiveSpellAction(
            id="sanctuary",
            name="Sanctuary",
            level=1,
            action_cost="bonus_action",
            range_ft=30,
            duration_minutes=1,
            target_policy="friendly",
            target_count=1,
            priority=32,
            modifier_effects=[
                SpellModifierEffect(
                    kind="targeting-save-gate",
                    save_ability="wisdom",
                    save_dc=save_dc,
                    ends_on_owner_attack=True,
                ),
            ],
            animation="sanctuary",
            source=f"{_SOURCE}: Sanctuary",
        )
    except Exception:
        logger.exception("Failed to build 2014 Sanctuary.")
        raise


def lesser_restoration_2014() -> ConditionRemovalAction:
    """Build shared 2014 Lesser Restoration through universal condition removal."""
    try:
        return ConditionRemovalAction(
            id="lesser-restoration",
            name="Lesser Restoration",
            action_cost="action",
            range_ft=5,
            target_mode="self_or_ally",
            removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
            removal_effect_tags=["disease"],
            spell_level=2,
            max_conditions_per_use=1,
            resource_costs={"spell-slot-2": 1},
            expends_spell_slot=True,
            animation="lesser-restoration",
        )
    except Exception:
        logger.exception("Failed to build 2014 Lesser Restoration.")
        raise


def aid_2014() -> DefensiveSpellAction:
    """Build base-slot 2014 Aid; higher-slot scaling is added only when explicitly supported."""
    try:
        return DefensiveSpellAction(
            id="aid",
            name="Aid",
            level=2,
            action_cost="action",
            range_ft=30,
            duration_minutes=480,
            target_policy="friendly",
            target_count=3,
            max_hp_increase=5,
            current_hp_increase=5,
            priority=40,
            animation="aid",
            source=f"{_SOURCE}: Aid",
        )
    except Exception:
        logger.exception("Failed to build 2014 Aid.")
        raise


def spiritual_weapon_2014(
    spell_attack_bonus: int,
    spellcasting_ability_modifier: int,
) -> PersistentSpellAttackAction:
    """Build 2014 Spiritual Weapon as one reusable mobile persistent spell attack."""
    try:
        attack = SpellAttackAction(
            id="spiritual-weapon",
            name="Spiritual Weapon",
            level=2,
            action_cost="bonus_action",
            attack_kind="melee",
            range_ft=60,
            attack_bonus=spell_attack_bonus,
            damage_dice_count=1,
            damage_dice_size=8,
            damage_bonus=spellcasting_ability_modifier,
            damage_type="force",
            animation="spiritual-weapon",
            source=f"{_SOURCE}: Spiritual Weapon",
        )
        return PersistentSpellAttackAction(
            id="spiritual-weapon",
            name="Spiritual Weapon",
            attack=attack,
            duration_rounds=10,
            move_ft=20,
            attack_reach_ft=5,
            upcast_interval_levels=2,
        )
    except Exception:
        logger.exception("Failed to build 2014 Spiritual Weapon.")
        raise


def beacon_of_hope_2014() -> DefensiveSpellAction:
    """Build shared 2014 Beacon of Hope from universal modifier primitives."""
    try:
        return DefensiveSpellAction(
            id="beacon-of-hope",
            name="Beacon of Hope",
            level=3,
            action_cost="action",
            range_ft=30,
            duration_minutes=1,
            target_policy="friendly",
            target_all_legal=True,
            concentration=True,
            priority=60,
            modifier_effects=[
                SpellModifierEffect(kind="saving-throw-advantage", save_ability="wisdom"),
                SpellModifierEffect(kind="death-save-advantage"),
                SpellModifierEffect(kind="healing-maximize"),
            ],
            animation="beacon-of-hope",
            source=f"{_SOURCE}: Beacon of Hope",
        )
    except Exception:
        logger.exception("Failed to build 2014 Beacon of Hope.")
        raise


def death_ward_2014() -> DefensiveSpellAction:
    """Build shared 2014 Death Ward on the universal zero-HP replacement modifier."""
    try:
        return DefensiveSpellAction(
            id="death-ward",
            name="Death Ward",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=480,
            target_policy="friendly",
            target_count=1,
            concentration=False,
            priority=95,
            modifier_effects=[
                SpellModifierEffect(
                    kind="zero-hp-replacement",
                    replacement_hp=1,
                    prevents_instant_death=True,
                ),
            ],
            animation="death-ward",
            source=f"{_SOURCE}: Death Ward",
        )
    except Exception:
        logger.exception("Failed to build 2014 Death Ward.")
        raise


def shield_2014() -> "DefensiveSpellAction":
    """Build 2014 Shield: reaction +5 AC until start of next turn."""
    from app.domain.spells import DefensiveSpellAction
    from app.domain.spell_modifiers import SpellModifierEffect
    try:
        return DefensiveSpellAction(
            id="shield", name="Shield", level=1, action_cost="reaction",
            range_ft=0, duration_rounds=1, target_policy="self",
            modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=5)],
            priority=40, animation="shield",
            source="D&D Basic Rules 2014: Shield",
        )
    except Exception:
        logger.exception("Failed to build 2014 Shield.")
        raise


def darkness_2014() -> "TimedSelfBuffAction":
    """Build 2014 Darkness as a timed self-buff that creates a darkness zone."""
    from app.domain.timed_self_buffs import TimedSelfBuffAction
    try:
        return TimedSelfBuffAction(
            id="darkness", name="Darkness", action_cost="action",
            resource_id="darkness", resource_cost=1, duration_rounds=100,
            expiry_timing="source_turn_end", concentration=True,
            animation="darkness",
        )
    except Exception:
        logger.exception("Failed to build 2014 Darkness.")
        raise


def mage_armor_2014() -> DefensiveSpellAction:
    """Build 2014 Mage Armor: base AC 13 + Dex."""
    try:
        return DefensiveSpellAction(
            id="mage-armor", name="Mage Armor", level=1, action_cost="action",
            range_ft=5, duration_minutes=480, target_policy="friendly",
            modifier_effects=[SpellModifierEffect(kind="armor-class-minimum", minimum_value=13)],
            priority=15, animation="mage-armor",
            source=f"{_SOURCE}: Mage Armor",
        )
    except Exception:
        logger.exception("Failed to build 2014 Mage Armor.")
        raise


def freedom_of_movement_2014() -> DefensiveSpellAction:
    """Build 2014 Freedom of Movement: immune to restrained/paralyzed/grappled."""
    try:
        return DefensiveSpellAction(
            id="freedom-of-movement", name="Freedom of Movement", level=4, action_cost="action",
            range_ft=5, duration_minutes=60, target_policy="friendly",
            modifier_effects=[
                SpellModifierEffect(kind="condition-immunity", condition_id="restrained"),
                SpellModifierEffect(kind="condition-immunity", condition_id="paralyzed"),
            ],
            priority=25, animation="freedom-of-movement",
            source=f"{_SOURCE}: Freedom of Movement",
        )
    except Exception:
        logger.exception("Failed to build 2014 Freedom of Movement.")
        raise


def counterspell_2014() -> "TimedSelfBuffAction":
    """Build 2014 Counterspell as a reaction that removes a spell effect."""
    from app.domain.timed_self_buffs import TimedSelfBuffAction
    try:
        return TimedSelfBuffAction(
            id="counterspell", name="Counterspell", action_cost="reaction",
            resource_id="counterspell", resource_cost=1, duration_rounds=1,
            expiry_timing="source_turn_end", animation="counterspell",
        )
    except Exception:
        logger.exception("Failed to build 2014 Counterspell.")
        raise


def gaseous_form_2014() -> "TimedSelfBuffAction":
    """Build 2014 Gaseous Form as a timed self-buff (form change, no combat stat change under locked Pit)."""
    from app.domain.timed_self_buffs import TimedSelfBuffAction
    try:
        return TimedSelfBuffAction(
            id="gaseous-form", name="Gaseous Form", action_cost="action",
            resource_id="gaseous-form", resource_cost=1, duration_rounds=600,
            expiry_timing="source_turn_end", concentration=True, animation="gaseous-form",
        )
    except Exception:
        logger.exception("Failed to build 2014 Gaseous Form.")
        raise


def globe_of_invulnerability_2014() -> "TimedSelfBuffAction":
    """Build 2014 Globe of Invulnerability as a timed self-buff."""
    from app.domain.timed_self_buffs import TimedSelfBuffAction
    try:
        return TimedSelfBuffAction(
            id="globe-of-invulnerability", name="Globe of Invulnerability", level=6,
            action_cost="action", resource_id="globe-of-invulnerability", resource_cost=1,
            duration_rounds=10, expiry_timing="source_turn_end", concentration=True,
            animation="globe-of-invulnerability",
        )
    except Exception:
        logger.exception("Failed to build 2014 Globe of Invulnerability.")
        raise


def fog_cloud_2014() -> "TimedSelfBuffAction":
    """Build 2014 Fog Cloud as a timed zone buff."""
    from app.domain.timed_self_buffs import TimedSelfBuffAction
    try:
        return TimedSelfBuffAction(
            id="fog-cloud", name="Fog Cloud", level=1, action_cost="action",
            resource_id="fog-cloud", resource_cost=1, duration_rounds=600,
            expiry_timing="source_turn_end", concentration=True, animation="fog-cloud",
        )
    except Exception:
        logger.exception("Failed to build 2014 Fog Cloud.")
        raise


def calm_emotions_2014(save_dc: int) -> "SpellSaveAction":
    """Build 2014 Calm Emotions: Wisdom save, suppress charm/frighten."""
    from app.domain.spells import SpellSaveAction
    from app.domain.save_effects import FailedSaveTimedEffect
    try:
        return SpellSaveAction(
            id="calm-emotions", name="Calm Emotions", level=2, action_cost="action",
            range_ft=60, save_ability="wisdom", dc=save_dc,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="calmed", duration_rounds=10, expiry_timing="source_turn_end",
            ),
            concentration=True, duration_minutes=1, animation="calm-emotions",
        )
    except Exception:
        logger.exception("Failed to build 2014 Calm Emotions.")
        raise
