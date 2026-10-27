from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def vicious_mockery_action_2014(save_dc: int, dice_count: int = 1) -> SpellSaveAction:
    """Build source-neutral 2014 Vicious Mockery from its declared DC and scaling."""
    try:
        if save_dc < 1 or dice_count not in range(1, 5):
            raise ValueError("2014 Vicious Mockery requires a positive DC and 1-4 dice.")
        return SpellSaveAction(
            id="vicious-mockery",
            name="Vicious Mockery",
            level=0,
            action_cost="action",
            range_ft=60,
            save_ability="wisdom",
            dc=save_dc,
            damage_dice_count=dice_count,
            damage_dice_size=4,
            damage_type="psychic",
            success_damage="none",
            requires_target_hearing=True,
            requires_target_sight=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="vicious-mockery-disadvantage",
                expiry_timing="target_turn_end",
                next_attack_disadvantage=True,
            ),
            animation="vicious-mockery",
        )
    except Exception:
        logger.exception("Failed to build 2014 Vicious Mockery for DC %s.", save_dc)
        raise


def vicious_mockery_2014(level: int, charisma_modifier: int) -> SpellSaveAction:
    """Build hero Vicious Mockery using 2014 cantrip scaling and spell-save math."""
    if level not in range(1, 21):
        raise ValueError("2014 Vicious Mockery supports character levels 1 through 20.")
    dice_count = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
    return vicious_mockery_action_2014(
        8 + proficiency_bonus(level) + charisma_modifier,
        dice_count,
    )
