from __future__ import annotations

import logging

from app.domain.actions import HealingAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect, SpellSaveAction

logger = logging.getLogger(__name__)


def healing_word_2014(wisdom_modifier: int, life_bonus: int) -> HealingAction:
    try:
        return HealingAction(
            id="healing-word", name="Healing Word", action_cost="bonus_action",
            range_ft=60, target_mode="self_or_ally", dice_count=1, dice_size=4,
            healing_bonus=wisdom_modifier + life_bonus,
            resource_id="spell-slot-1", resource_cost=1, animation="healing",
        )
    except Exception:
        logger.exception("Failed to build 2014 Healing Word.")
        raise


def cure_wounds_2014(wisdom_modifier: int, life_bonus: int) -> HealingAction:
    try:
        return HealingAction(
            id="cure-wounds", name="Cure Wounds", action_cost="action",
            range_ft=5, target_mode="self_or_ally", dice_count=1, dice_size=8,
            healing_bonus=wisdom_modifier + life_bonus,
            resource_id="spell-slot-1", resource_cost=1, animation="healing",
        )
    except Exception:
        logger.exception("Failed to build 2014 Cure Wounds.")
        raise


def guiding_bolt_2014(attack_bonus: int) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="guiding-bolt", name="Guiding Bolt", level=1, action_cost="action",
            attack_kind="ranged", range_ft=120, attack_bonus=attack_bonus,
            damage_dice_count=4, damage_dice_size=6, damage_type="radiant",
            on_hit_modifier_effects=[SpellModifierEffect(
                kind="attacks-against-advantage",
                consume_on_attack_against=True,
                expires_after_source_turns=1,
            )],
            animation="guiding-bolt",
            source="D&D Basic Rules 2014: Guiding Bolt",
        )
    except Exception:
        logger.exception("Failed to build 2014 Guiding Bolt.")
        raise


def inflict_wounds_2014(attack_bonus: int) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="inflict-wounds", name="Inflict Wounds", level=1, action_cost="action",
            attack_kind="melee", range_ft=5, attack_bonus=attack_bonus,
            damage_dice_count=3, damage_dice_size=10, damage_type="necrotic",
            animation="spell-attack",
            source="D&D Basic Rules 2014: Inflict Wounds",
        )
    except Exception:
        logger.exception("Failed to build 2014 Inflict Wounds.")
        raise


def sacred_flame_2014(save_dc: int, character_level: int = 1) -> SpellSaveAction:
    try:
        if not 1 <= character_level <= 20:
            raise ValueError("Sacred Flame character level must be between 1 and 20.")
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellSaveAction(
            id="sacred-flame", name="Sacred Flame", level=0, action_cost="action",
            range_ft=60, save_ability="dexterity", dc=save_dc,
            damage_dice_count=dice_count, damage_dice_size=8, damage_type="radiant",
            success_damage="none", animation="sacred-flame",
        )
    except Exception:
        logger.exception("Failed to build 2014 Sacred Flame.")
        raise


def bless_2014() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="bless", name="Bless", level=1, action_cost="action",
            range_ft=30, duration_minutes=1, target_policy="friendly", target_count=3,
            modifier_effects=[
                SpellModifierEffect(kind="attack-roll-bonus-die", dice_count=1, dice_size=4),
                SpellModifierEffect(kind="saving-throw-bonus-die", dice_count=1, dice_size=4),
            ],
            concentration=True, priority=30, animation="bless",
            source="D&D Basic Rules 2014: Bless",
        )
    except Exception:
        logger.exception("Failed to build 2014 Bless.")
        raise


def shield_of_faith_2014() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="shield-of-faith", name="Shield of Faith", level=1,
            action_cost="bonus_action", range_ft=60, duration_minutes=10,
            target_policy="friendly",
            modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=2)],
            concentration=True, priority=20, animation="shield-of-faith",
            source="D&D Basic Rules 2014: Shield of Faith",
        )
    except Exception:
        logger.exception("Failed to build 2014 Shield of Faith.")
        raise
