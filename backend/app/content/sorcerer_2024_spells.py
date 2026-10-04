from __future__ import annotations

import logging

from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.spells import SpellAttackAction, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def magic_missile_2024() -> AutoHitSpellAction:
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
            source="D&D Beyond Basic Rules 2024: Magic Missile",
        )
    except Exception:
        logger.exception("Failed to build 2024 Magic Missile.")
        raise


def lightning_bolt_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="lightning-bolt",
            name="Lightning Bolt",
            level=3,
            action_cost="action",
            range_ft=100,
            area=AreaTargeting(shape="line", origin="self", length_ft=100, width_ft=5),
            save_ability="dexterity",
            dc=save_dc,
            damage_dice_count=8,
            damage_dice_size=6,
            damage_type="lightning",
            success_damage="half",
            upcast_dice_per_level=1,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Failed to build 2024 Lightning Bolt.")
        raise


def chromatic_orb_2024(attack_bonus: int, damage_bonus: int = 0) -> SpellAttackAction:
    """2024 Chromatic Orb primary hit. Matching-dice leap remains unbound."""
    try:
        return SpellAttackAction(
            id="chromatic-orb",
            name="Chromatic Orb",
            level=1,
            action_cost="action",
            attack_kind="ranged",
            range_ft=90,
            attack_bonus=attack_bonus,
            damage_dice_count=3,
            damage_dice_size=8,
            damage_bonus=damage_bonus,
            damage_type="fire",
            animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Chromatic Orb",
        )
    except Exception:
        logger.exception("Failed to build 2024 Chromatic Orb.")
        raise
