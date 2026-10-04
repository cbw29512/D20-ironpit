from __future__ import annotations

import logging

from app.domain.post_hit_save_condition import PostHitSaveConditionSpell
from app.domain.size import CreatureSize
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction

logger = logging.getLogger(__name__)


def hunters_mark_2024(*, dice_size: int = 6) -> TargetedConcentrationDamageAction:
    try:
        if dice_size not in {6, 10}:
            raise ValueError("2024 Hunter's Mark uses a d6, or a d10 with Foe Slayer.")
        return TargetedConcentrationDamageAction(
            id="hunters-mark",
            name="Hunter's Mark",
            level=1,
            action_cost="bonus_action",
            range_ft=90,
            dice_count=1,
            dice_size=dice_size,
            damage_type="force",
            duration_rounds_by_slot={1: 600, 3: 4800, 5: 14400},
            retarget_after_target_zero=True,
            free_cast_resource_id="favored-enemy-hunters-mark",
            free_cast_resource_cost=1,
            priority=20,
            animation="targeted-concentration",
            source="D&D Beyond Basic Rules 2024: Hunter's Mark",
        )
    except Exception:
        logger.exception("Failed to compile 2024 Hunter's Mark.")
        raise


def ensnaring_strike_2024(save_dc: int) -> PostHitSaveConditionSpell:
    try:
        if save_dc < 1:
            raise ValueError("Ensnaring Strike requires a positive spell save DC.")
        return PostHitSaveConditionSpell(
            id="ensnaring-strike",
            name="Ensnaring Strike",
            level=1,
            action_cost="bonus_action",
            save_ability="strength",
            save_dc=save_dc,
            failed_condition_id="restrained",
            duration_rounds=10,
            concentration=True,
            success_ends_spell=True,
            size_save_advantage_from=CreatureSize.LARGE,
            start_of_turn_dice_count=1,
            start_of_turn_dice_per_slot_above=1,
            start_of_turn_dice_size=6,
            start_of_turn_damage_type="piercing",
            escape_skill="athletics",
            escape_action_cost="action",
            priority=25,
            animation="ensnaring-strike",
            source="D&D Beyond Basic Rules 2024: Ensnaring Strike",
        )
    except Exception:
        logger.exception("Failed to compile 2024 Ensnaring Strike.")
        raise
