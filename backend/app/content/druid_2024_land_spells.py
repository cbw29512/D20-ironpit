from __future__ import annotations

import logging

from app.content.offensive_spell_effects import cantrip_damage_dice
from app.domain.actions import AreaHealingRider, SavingThrowAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_lands_aid_2024(save_dc: int, character_level: int) -> SavingThrowAction:
    try:
        dice_count = 2 + int(character_level >= 10) + int(character_level >= 14)
        return SavingThrowAction(
            id="lands-aid", name="Land's Aid", action_cost="action",
            save_ability="constitution", dc=save_dc, range_ft=60,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
            damage_dice_count=dice_count, damage_dice_size=6,
            damage_type="necrotic", success_damage="half",
            resource_id="wild-shape", resource_cost=1, magical_effect=True,
            area_healing_rider=AreaHealingRider(dice_count=dice_count, dice_size=6),
            animation="lands-aid",
        )
    except Exception:
        logger.exception("Failed to build 2024 Land's Aid at Druid level %s.", character_level)
        raise


def build_fire_bolt_2024(
    attack_bonus: int,
    character_level: int,
    damage_bonus: int = 0,
) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="fire-bolt", name="Fire Bolt", level=0, action_cost="action",
            attack_kind="ranged", range_ft=120, attack_bonus=attack_bonus,
            damage_dice_count=cantrip_damage_dice(character_level), damage_dice_size=10,
            damage_bonus=damage_bonus, damage_type="fire", animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Fire Bolt",
        )
    except Exception:
        logger.exception("Failed to build 2024 Fire Bolt at level %s.", character_level)
        raise


def build_burning_hands_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="burning-hands", name="Burning Hands", level=1, action_cost="action",
            range_ft=15, area=AreaTargeting(shape="cone", origin="self", length_ft=15),
            save_ability="dexterity", dc=save_dc, damage_dice_count=3,
            damage_dice_size=6, damage_type="fire", success_damage="half",
            upcast_dice_per_level=1, animation="burning-hands",
            source="D&D Beyond Basic Rules 2024: Burning Hands",
        )
    except Exception:
        logger.exception("Failed to build 2024 Burning Hands.")
        raise


def build_blight_2024(save_dc: int) -> SpellSaveAction:
    """Explicit 2024 Blight fingerprint using the universal save pipeline."""
    try:
        return SpellSaveAction(
            id="blight",
            name="Blight",
            level=4,
            action_cost="action",
            range_ft=30,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=8,
            damage_dice_size=8,
            damage_type="necrotic",
            success_damage="half",
            upcast_dice_per_level=1,
            automatic_failure_creature_types=["Plant"],
            requires_target_sight=True,
            animation="blight",
            source="D&D Beyond Basic Rules 2024: Blight",
        )
    except Exception:
        logger.exception("Failed to build 2024 Blight.")
        raise


def build_blur_2024() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="blur", name="Blur", level=2, action_cost="action", range_ft=0,
            duration_minutes=1, target_policy="self", target_count=1,
            modifier_effects=[SpellModifierEffect(
                kind="attacks-against-disadvantage",
                bypass_attacker_senses=["blindsight", "truesight"],
            )],
            concentration=True, priority=70, animation="blur",
            source="D&D Beyond Basic Rules 2024: Blur",
        )
    except Exception:
        logger.exception("Failed to build 2024 Blur.")
        raise
