from __future__ import annotations

import logging

from app.content.offensive_spell_effects import cantrip_damage_dice
from app.domain.actions import AreaHealingRider, SavingThrowAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_poison_spray_2024(attack_bonus: int, character_level: int) -> SpellAttackAction:
    """Explicit 2024 Poison Spray fingerprint."""
    try:
        return SpellAttackAction(
            id="poison-spray",
            name="Poison Spray",
            level=0,
            action_cost="action",
            attack_kind="ranged",
            range_ft=30,
            attack_bonus=attack_bonus,
            damage_dice_count=cantrip_damage_dice(character_level),
            damage_dice_size=12,
            damage_type="poison",
            animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Poison Spray",
        )
    except Exception:
        logger.exception("Failed to build 2024 Poison Spray at level %s.", character_level)
        raise


def build_longstrider_2024() -> DefensiveSpellAction:
    """Explicit 2024 Longstrider fingerprint."""
    try:
        return DefensiveSpellAction(
            id="longstrider",
            name="Longstrider",
            level=1,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            target_count_per_slot_above=1,
            modifier_effects=[SpellModifierEffect(kind="speed", flat_bonus=10)],
            concentration=False,
            priority=15,
            animation="longstrider",
            source="D&D Beyond Basic Rules 2024: Longstrider",
        )
    except Exception:
        logger.exception("Failed to build 2024 Longstrider.")
        raise


def build_faerie_fire_2024(save_dc: int) -> SpellSaveAction:
    """Explicit 2024 Faerie Fire fingerprint using shared area-save modifiers."""
    try:
        return SpellSaveAction(
            id="faerie-fire",
            name="Faerie Fire",
            level=1,
            action_cost="action",
            range_ft=60,
            area=AreaTargeting(shape="cube", origin="point", length_ft=20),
            save_ability="dexterity",
            dc=save_dc,
            damage_dice_count=0,
            damage_type=None,
            success_damage="none",
            failed_save_modifier_effects=[
                SpellModifierEffect(kind="attacks-against-advantage"),
                SpellModifierEffect(kind="invisibility-benefits-suppressed"),
            ],
            concentration=True,
            duration_minutes=1,
            animation="faerie-fire",
            source="D&D Beyond Basic Rules 2024: Faerie Fire",
        )
    except Exception:
        logger.exception("Failed to build 2024 Faerie Fire.")
        raise


def build_lands_aid_2024(save_dc: int, character_level: int) -> SavingThrowAction:
    """2024 Circle of the Land Land's Aid through the shared area-save/healing rider."""
    try:
        dice_count = 2 + int(character_level >= 10) + int(character_level >= 14)
        return SavingThrowAction(
            id="lands-aid",
            name="Land's Aid",
            action_cost="action",
            save_ability="constitution",
            dc=save_dc,
            range_ft=60,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
            damage_dice_count=dice_count,
            damage_dice_size=6,
            damage_type="necrotic",
            success_damage="half",
            resource_id="wild-shape",
            resource_cost=1,
            magical_effect=True,
            area_healing_rider=AreaHealingRider(
                dice_count=dice_count,
                dice_size=6,
            ),
            animation="lands-aid",
        )
    except Exception:
        logger.exception("Failed to build 2024 Land's Aid at Druid level %s.", character_level)
        raise
