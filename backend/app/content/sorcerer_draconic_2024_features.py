from __future__ import annotations

import logging

from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment
from app.domain.movement import MovementModeGrant
from app.domain.progression import ProgressionCombatFeatures
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def innate_sorcery_2024() -> TimedSelfBuffAction:
    try:
        return TimedSelfBuffAction(
            id="innate-sorcery",
            name="Innate Sorcery",
            action_cost="bonus_action",
            resource_id="innate-sorcery",
            resource_cost=1,
            duration_rounds=10,
            spell_save_dc_bonus=1,
            spell_attack_advantage=True,
            expiry_timing="source_turn_start",
            priority=95,
            animation="innate-sorcery",
        )
    except Exception:
        logger.exception("Failed to build 2024 Innate Sorcery.")
        raise


def innate_sorcery_incarnate_2024() -> TimedSelfBuffAction:
    try:
        return TimedSelfBuffAction(
            id="innate-sorcery",
            name="Innate Sorcery",
            action_cost="bonus_action",
            resource_id="sorcery-points",
            resource_cost=2,
            duration_rounds=10,
            spell_save_dc_bonus=1,
            spell_attack_advantage=True,
            expiry_timing="source_turn_start",
            priority=80,
            animation="innate-sorcery",
        )
    except Exception:
        logger.exception("Failed to build 2024 Sorcery Incarnate Innate Sorcery.")
        raise


def dragon_wings_2024() -> TimedSelfBuffAction:
    try:
        return TimedSelfBuffAction(
            id="dragon-wings",
            name="Dragon Wings",
            action_cost="bonus_action",
            resource_id="dragon-wings",
            resource_cost=1,
            duration_rounds=600,
            movement_mode_grants=[MovementModeGrant(mode="fly", fixed_speed_ft=60)],
            expiry_timing="source_turn_start",
            priority=80,
            animation="dragon-wings",
        )
    except Exception:
        logger.exception("Failed to build 2024 Dragon Wings.")
        raise


def dragon_wings_restore_2024() -> ResourceConversionAction:
    try:
        return ResourceConversionAction(
            id="dragon-wings-restore",
            name="Dragon Wings",
            action_cost="none",
            source_resource_id="sorcery-points",
            source_cost=3,
            target_resource_id="dragon-wings",
            target_gain=1,
            requires_target_empty=True,
            automation="when-target-empty",
            source="D&D Beyond Basic Rules 2024: Draconic Sorcery, Dragon Wings",
        )
    except Exception:
        logger.exception("Failed to build 2024 Dragon Wings restore.")
        raise


def build_sorcerer_2024_features(level: int) -> ProgressionCombatFeatures:
    try:
        return ProgressionCombatFeatures(
            resource_backed_d20_outcome_adjustments=(
                [ResourceBackedD20OutcomeAdjustment(
                    source_id="boon-of-fate",
                    source_name="Boon of Fate",
                    resource_id="boon-of-fate",
                    dice_count=2,
                    dice_size=4,
                    range_ft=60,
                    test_kinds=["attack", "saving_throw", "ability_check"],
                    can_add=True,
                    can_subtract=True,
                )] if level >= 19 else []
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Sorcerer features at level %s.", level)
        raise
