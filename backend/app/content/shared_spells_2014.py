from __future__ import annotations

import logging

from app.domain.actions import ConditionRemovalAction
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellModifierEffect

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014"


def sanctuary_2014(save_dc: int) -> DefensiveSpellAction:
    """Build shared 2014 Sanctuary through the universal targeting-save gate."""
    try:
        return DefensiveSpellAction(
            id="sanctuary",
            name="Sanctuary",
            level=1,
            action_cost="bonus_action",
            range_ft=30,
            duration_minutes=1,
            target_policy="friendly",
            target_count=1,
            priority=32,
            modifier_effects=[
                SpellModifierEffect(
                    kind="targeting-save-gate",
                    save_ability="wisdom",
                    save_dc=save_dc,
                    ends_on_owner_attack=True,
                ),
            ],
            animation="sanctuary",
            source=f"{_SOURCE}: Sanctuary",
        )
    except Exception:
        logger.exception("Failed to build 2014 Sanctuary.")
        raise


def lesser_restoration_2014() -> ConditionRemovalAction:
    """Build shared 2014 Lesser Restoration through universal condition removal."""
    try:
        return ConditionRemovalAction(
            id="lesser-restoration",
            name="Lesser Restoration",
            action_cost="action",
            range_ft=5,
            target_mode="self_or_ally",
            removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
            max_conditions_per_use=1,
            resource_costs={"spell-slot-2": 1},
            expends_spell_slot=True,
            animation="lesser-restoration",
        )
    except Exception:
        logger.exception("Failed to build 2014 Lesser Restoration.")
        raise


def aid_2014() -> DefensiveSpellAction:
    """Build base-slot 2014 Aid; higher-slot scaling is added only when explicitly supported."""
    try:
        return DefensiveSpellAction(
            id="aid",
            name="Aid",
            level=2,
            action_cost="action",
            range_ft=30,
            duration_minutes=480,
            target_policy="friendly",
            target_count=3,
            max_hp_increase=5,
            current_hp_increase=5,
            priority=40,
            animation="aid",
            source=f"{_SOURCE}: Aid",
        )
    except Exception:
        logger.exception("Failed to build 2014 Aid.")
        raise


def spiritual_weapon_2014(
    spell_attack_bonus: int,
    spellcasting_ability_modifier: int,
) -> PersistentSpellAttackAction:
    """Build 2014 Spiritual Weapon as one reusable mobile persistent spell attack."""
    try:
        attack = SpellAttackAction(
            id="spiritual-weapon",
            name="Spiritual Weapon",
            level=2,
            action_cost="bonus_action",
            attack_kind="melee",
            range_ft=60,
            attack_bonus=spell_attack_bonus,
            damage_dice_count=1,
            damage_dice_size=8,
            damage_bonus=spellcasting_ability_modifier,
            damage_type="force",
            animation="spiritual-weapon",
            source=f"{_SOURCE}: Spiritual Weapon",
        )
        return PersistentSpellAttackAction(
            id="spiritual-weapon",
            name="Spiritual Weapon",
            attack=attack,
            duration_rounds=10,
            move_ft=20,
            attack_reach_ft=5,
            upcast_interval_levels=2,
        )
    except Exception:
        logger.exception("Failed to build 2014 Spiritual Weapon.")
        raise


def beacon_of_hope_2014() -> DefensiveSpellAction:
    """Build shared 2014 Beacon of Hope from universal modifier primitives."""
    try:
        return DefensiveSpellAction(
            id="beacon-of-hope",
            name="Beacon of Hope",
            level=3,
            action_cost="action",
            range_ft=30,
            duration_minutes=1,
            target_policy="friendly",
            target_count=20,
            concentration=True,
            priority=60,
            modifier_effects=[
                SpellModifierEffect(kind="saving-throw-advantage", save_ability="wisdom"),
                SpellModifierEffect(kind="death-save-advantage"),
                SpellModifierEffect(kind="healing-maximize"),
            ],
            animation="beacon-of-hope",
            source=f"{_SOURCE}: Beacon of Hope",
        )
    except Exception:
        logger.exception("Failed to build 2014 Beacon of Hope.")
        raise
