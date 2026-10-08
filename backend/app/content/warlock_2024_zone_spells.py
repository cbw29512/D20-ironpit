from __future__ import annotations

import logging

from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_SOURCE = "D&D Beyond Basic Rules 2024"


def stinking_cloud_2024(save_dc: int, pact_slot_level: int) -> PersistentSaveZoneAction:
    """2024 Stinking Cloud: start-of-turn Con save or Poisoned and no Action/Bonus Action."""
    try:
        return PersistentSaveZoneAction(
            id="stinking-cloud",
            name="Stinking Cloud",
            level=3,
            action_cost="action",
            cast_range_ft=90,
            radius_ft=20,
            duration_rounds=10,
            concentration=True,
            save_ability="constitution",
            dc=save_dc,
            triggers=["start_turn"],
            failed_save_condition_id="poisoned",
            failed_save_duration_rounds=1,
            failed_save_suppress_action=True,
            failed_save_suppress_bonus_action=True,
            resource_id=f"spell-slot-{pact_slot_level}",
            expends_spell_slot=True,
            animation="stinking-cloud",
            source=f"{_SOURCE}: Stinking Cloud",
        )
    except Exception:
        logger.exception("Failed to build 2024 Stinking Cloud.")
        raise


def insect_plague_2024(save_dc: int, pact_slot_level: int) -> PersistentSaveZoneAction:
    """2024 Insect Plague: 20-foot sphere, Con save 4d10 piercing, appear/enter/end, once per turn."""
    try:
        return PersistentSaveZoneAction(
            id="insect-plague",
            name="Insect Plague",
            level=5,
            action_cost="action",
            cast_range_ft=300,
            radius_ft=20,
            duration_rounds=100,
            concentration=True,
            save_ability="constitution",
            dc=save_dc,
            triggers=["appear", "enter", "end_turn"],
            damage_dice_count=4,
            damage_dice_size=10,
            damage_type="piercing",
            success_damage="half",
            upcast_dice_per_level=1,
            resource_id=f"spell-slot-{pact_slot_level}",
            expends_spell_slot=True,
            animation="insect-plague",
            source=f"{_SOURCE}: Insect Plague",
        )
    except Exception:
        logger.exception("Failed to build 2024 Insect Plague.")
        raise


def wall_of_fire_2024(save_dc: int, pact_slot_level: int) -> PersistentSaveZoneAction:
    """2024 Wall of Fire using the printed ringed wall, damaging the inner side."""
    try:
        return PersistentSaveZoneAction(
            id="wall-of-fire",
            name="Wall of Fire",
            level=4,
            action_cost="action",
            cast_range_ft=120,
            radius_ft=10,
            duration_rounds=10,
            concentration=True,
            save_ability="dexterity",
            dc=save_dc,
            triggers=["appear", "enter", "end_turn"],
            save_triggers=["appear"],
            damage_dice_count=5,
            damage_dice_size=8,
            damage_type="fire",
            success_damage="half",
            upcast_dice_per_level=1,
            resource_id=f"spell-slot-{pact_slot_level}",
            expends_spell_slot=True,
            animation="wall-of-fire",
            source=f"{_SOURCE}: Wall of Fire",
        )
    except Exception:
        logger.exception("Failed to build 2024 Wall of Fire.")
        raise


def fire_shield_2024(pact_slot_level: int) -> list[TimedSelfBuffAction]:
    """2024 Fire Shield: warm or chill, 10 minutes, resistance plus 2d8 melee retaliation."""
    try:
        return [
            TimedSelfBuffAction(
                id="fire-shield-warm",
                name="Fire Shield",
                action_cost="action",
                resource_id=f"spell-slot-{pact_slot_level}",
                resource_cost=1,
                duration_rounds=100,
                damage_resistances=[DamageType.COLD],
                melee_hit_retaliation=MeleeHitRetaliation(
                    range_ft=5, dice_count=2, dice_size=8, damage_type=DamageType.FIRE,
                ),
                ends_if_source_dead=True,
                expiry_timing="source_turn_end",
                priority=88,
                selection_group="fire-shield-variants", selection_strategy="incoming-damage",
                animation="fire-shield",
            ),
            TimedSelfBuffAction(
                id="fire-shield-chill",
                name="Fire Shield",
                action_cost="action",
                resource_id=f"spell-slot-{pact_slot_level}",
                resource_cost=1,
                duration_rounds=100,
                damage_resistances=[DamageType.FIRE],
                melee_hit_retaliation=MeleeHitRetaliation(
                    range_ft=5, dice_count=2, dice_size=8, damage_type=DamageType.COLD,
                ),
                ends_if_source_dead=True,
                expiry_timing="source_turn_end",
                priority=87,
                selection_group="fire-shield-variants", selection_strategy="incoming-damage",
                animation="fire-shield",
            ),
        ]
    except Exception:
        logger.exception("Failed to build 2024 Fire Shield.")
        raise
