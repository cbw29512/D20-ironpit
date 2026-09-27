from __future__ import annotations

import logging

from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.hit_effects import OnHitTimedEffect
from app.domain.spells import DefensiveSpellAction, SpellAttackAction

logger = logging.getLogger(__name__)


def false_life_2014() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="false-life",
            name="False Life",
            level=1,
            action_cost="action",
            range_ft=0,
            duration_minutes=60,
            target_policy="self",
            temporary_hp=7,
            temporary_hp_per_slot_above=5,
            priority=70,
            animation="false-life",
            source="D&D Basic Rules 2014: False Life",
        )
    except Exception:
        logger.exception("Failed to build 2014 False Life.")
        raise


def magic_missile_2014() -> AutoHitSpellAction:
    try:
        return AutoHitSpellAction(
            id="magic-missile",
            name="Magic Missile",
            level=1,
            action_cost="action",
            range_ft=120,
            projectile_count=3,
            projectiles_per_slot_above=1,
            damage_dice_count=1,
            damage_dice_size=4,
            damage_bonus=1,
            damage_type="force",
            animation="magic-missile",
            source="D&D Basic Rules 2014: Magic Missile",
        )
    except Exception:
        logger.exception("Failed to build 2014 Magic Missile.")
        raise


def shocking_grasp_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        dice_count = 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
        return SpellAttackAction(
            id="shocking-grasp",
            name="Shocking Grasp",
            level=0,
            action_cost="action",
            attack_kind="melee",
            range_ft=5,
            attack_bonus=attack_bonus,
            damage_dice_count=dice_count,
            damage_dice_size=8,
            damage_type="lightning",
            advantage_if_target_wearing_metal_armor=True,
            on_hit_timed_effects=[
                OnHitTimedEffect(
                    effect_id="reaction-suppressed",
                    duration_rounds=1,
                    expiry_timing="source_turn_start",
                    suppress_reactions=True,
                    source_is_magical=True,
                )
            ],
            animation="shocking-grasp",
            source="D&D Basic Rules 2014: Shocking Grasp",
        )
    except Exception:
        logger.exception("Failed to build 2014 Shocking Grasp.")
        raise
