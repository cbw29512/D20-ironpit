from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction
from app.domain.suppression_zones import PersistentSuppressionZoneAction
from app.domain.timed_self_buffs import TimedEmanationDamage, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"


def hold_person_2014(save_dc: int) -> SpellSaveAction:
    """Build 2014 Hold Person: seen humanoid, Wisdom save, paralyzed, repeat save each turn."""
    try:
        return SpellSaveAction(
            id="hold-person",
            name="Hold Person",
            level=2,
            action_cost="action",
            range_ft=60,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            required_target_creature_types=["humanoid"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="paralyzed",
                duration_rounds=10,
                expiry_timing="target_turn_end",
                repeat_save_ability="wisdom",
                repeat_save_dc=save_dc,
                repeat_save_timing="target_turn_end",
            ),
            concentration=True,
            duration_minutes=1,
            animation="hold-person",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Hold Person.")
        raise


def silence_2014() -> PersistentSuppressionZoneAction:
    """Build 2014 Silence: 20-foot sphere that deafens, blocks verbal spells, and stops thunder."""
    try:
        return PersistentSuppressionZoneAction(
            id="silence",
            name="Silence",
            level=2,
            action_cost="action",
            cast_range_ft=120,
            radius_ft=20,
            duration_rounds=100,
            concentration=True,
            deafens=True,
            blocks_verbal_spells=True,
            thunder_immunity=True,
            resource_id="spell-slot-2",
            expends_spell_slot=True,
            animation="silence",
            source=f"{_SOURCE}: Silence",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Silence.")
        raise


def spirit_guardians_2014(save_dc: int) -> TimedSelfBuffAction:
    """Build 2014 Spirit Guardians as a 15-foot enter-or-start Wisdom-save radiant emanation."""
    try:
        return TimedSelfBuffAction(
            id="spirit-guardians",
            name="Spirit Guardians",
            action_cost="action",
            resource_id="spell-slot-3",
            resource_cost=1,
            duration_rounds=100,
            start_turn_emanation_damage=TimedEmanationDamage(
                trigger="enter_or_start",
                radius_ft=15,
                dice_count=3,
                dice_size=8,
                damage_type=DamageType.RADIANT,
                save_ability="wisdom",
                save_dc=save_dc,
                success_damage="half",
                speed_multiplier=0.5,
            ),
            concentration=True,
            ends_if_source_dead=True,
            expiry_timing="source_turn_start",
            priority=88,
            animation="spirit-guardians",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Spirit Guardians.")
        raise
