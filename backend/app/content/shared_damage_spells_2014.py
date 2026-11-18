from __future__ import annotations

import logging

from app.domain.save_damage import SaveDamageComponent
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def flame_strike_2014(save_dc: int) -> SpellSaveAction:
    """Build source-neutral 2014 Flame Strike with independent damage components."""
    try:
        return SpellSaveAction(
            id="flame-strike",
            name="Flame Strike",
            level=5,
            action_cost="action",
            range_ft=60,
            area_radius_ft=10,
            save_ability="dexterity",
            dc=save_dc,
            success_damage="half",
            damage_components=[
                SaveDamageComponent(
                    dice_count=4, dice_size=6, damage_type="fire", upcast_dice_per_level=1,
                ),
                SaveDamageComponent(dice_count=4, dice_size=6, damage_type="radiant"),
            ],
            animation="flame-strike",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Flame Strike.")
        raise


def harm_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Harm: 14d6 necrotic, Constitution half, floor 1 HP, failed-save max-HP loss."""
    try:
        return SpellSaveAction(
            id="harm",
            name="Harm",
            level=6,
            action_cost="action",
            range_ft=60,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=14,
            damage_dice_size=6,
            damage_type="necrotic",
            success_damage="half",
            requires_target_sight=True,
            excluded_target_creature_types=["undead", "construct"],
            minimum_remaining_hp=1,
            reduce_hit_point_maximum_on_failed_save=True,
            animation="harm",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Harm.")
        raise


def finger_of_death_spell_2014(save_dc: int) -> SpellSaveAction:
    """Build the shared 2014 Finger of Death save/damage spell.

    The printed Humanoid zombie rider is arena-inert under the locked
    no-extra-combatants rule; damage remains fully executable.
    """
    try:
        return SpellSaveAction(
            id="finger-of-death",
            name="Finger of Death",
            level=7,
            action_cost="action",
            range_ft=60,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=7,
            damage_dice_size=8,
            damage_bonus=30,
            damage_type="necrotic",
            success_damage="half",
            requires_target_sight=True,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Finger of Death.")
        raise

