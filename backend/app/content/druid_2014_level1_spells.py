from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect, SpellSaveAction

logger = logging.getLogger(__name__)


def produce_flame_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        if not 1 <= character_level <= 20:
            raise ValueError("Produce Flame character level must be between 1 and 20.")
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellAttackAction(
            id="produce-flame", name="Produce Flame", level=0, action_cost="action",
            attack_kind="ranged", range_ft=30, attack_bonus=attack_bonus,
            damage_dice_count=dice_count, damage_dice_size=8, damage_type="fire",
            animation="spell-attack", source="D&D Basic Rules 2014: Produce Flame",
        )
    except Exception:
        logger.exception("Failed to build 2014 Produce Flame at level %s.", character_level)
        raise


def poison_spray_2014(save_dc: int, character_level: int) -> SpellSaveAction:
    try:
        if not 1 <= character_level <= 20:
            raise ValueError("Poison Spray character level must be between 1 and 20.")
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellSaveAction(
            id="poison-spray", name="Poison Spray", level=0, action_cost="action",
            range_ft=10, save_ability="constitution", dc=save_dc,
            damage_dice_count=dice_count, damage_dice_size=12, damage_type="poison",
            success_damage="none", animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2014 Poison Spray at level %s.", character_level)
        raise


def longstrider_2014() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="longstrider", name="Longstrider", level=1, action_cost="action",
            range_ft=5, duration_minutes=60, target_policy="friendly", target_count=1,
            modifier_effects=[SpellModifierEffect(kind="speed", flat_bonus=10)],
            concentration=False, priority=15, animation="longstrider",
            source="D&D Basic Rules 2014: Longstrider",
        )
    except Exception:
        logger.exception("Failed to build 2014 Longstrider.")
        raise
