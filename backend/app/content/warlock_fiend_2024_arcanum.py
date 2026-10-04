from __future__ import annotations

import logging

from app.content.threshold_spell_effects import build_power_word_kill_2024
from app.domain.actions import HpThresholdConditionAction, SavingThrowAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def build_varek_2024_arcanum_saves(level: int, save_dc: int) -> list[SavingThrowAction]:
    try:
        actions: list[SavingThrowAction] = []
        if level >= 11:
            actions.append(SavingThrowAction(
                id="circle-of-death",
                name="Circle of Death",
                save_ability="constitution",
                dc=save_dc,
                range_ft=150,
                area=AreaTargeting(shape="radius", origin="point", radius_ft=60),
                damage_dice_count=8,
                damage_dice_size=8,
                damage_type="necrotic",
                success_damage="half",
                resource_id="mystic-arcanum-6",
                resource_cost=1,
                magical_effect=True,
                animation="spell-save",
            ))
        if level >= 13:
            actions.append(SavingThrowAction(
                id="finger-of-death",
                name="Finger of Death",
                save_ability="constitution",
                dc=save_dc,
                range_ft=60,
                damage_dice_count=7,
                damage_dice_size=8,
                damage_bonus=30,
                damage_type="necrotic",
                success_damage="half",
                resource_id="mystic-arcanum-7",
                resource_cost=1,
                magical_effect=True,
                animation="spell-save",
            ))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Varek Mystic Arcanum saves at level %s.", level)
        raise


def build_varek_2024_power_word_stun(save_dc: int) -> HpThresholdConditionAction:
    try:
        return HpThresholdConditionAction(
            id="power-word-stun",
            name="Power Word Stun",
            action_cost="action",
            range_ft=60,
            requires_target_sight=True,
            max_current_hp=150,
            condition_id="stunned",
            repeat_save_ability="constitution",
            repeat_save_dc=save_dc,
            repeat_save_timing="target_turn_end",
            resource_id="mystic-arcanum-8",
            resource_cost=1,
            magical_effect=True,
            animation="spell-condition",
        )
    except Exception:
        logger.exception("Failed to build 2024 Power Word Stun.")
        raise


def build_varek_2024_threshold_death(level: int):
    try:
        if level < 17:
            return []
        return [build_power_word_kill_2024().model_copy(update={"resource_id": "mystic-arcanum-9"})]
    except Exception:
        logger.exception("Failed to build 2024 Varek Power Word Kill at level %s.", level)
        raise
