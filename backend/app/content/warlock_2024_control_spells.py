from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Beyond Basic Rules 2024"


def hold_person_2024(save_dc: int) -> SpellSaveAction:
    """2024 Hold Person: seen humanoid, Wisdom save, paralyzed, extra target per slot above 2."""
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
            allows_higher_slots=True,
            target_count=1,
            target_count_per_slot_above=1,
            animation="hold-person",
        )
    except Exception:
        logger.exception("Failed to build 2024 Hold Person.")
        raise


def command_2024(save_dc: int) -> SpellSaveAction:
    """2024 Command Grovel: Wisdom save, Prone, then the target's next turn ends."""
    try:
        return SpellSaveAction(
            id="command",
            name="Command",
            level=1,
            action_cost="action",
            range_ft=60,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="prone",
                duration_rounds=1,
                expiry_timing="target_turn_end",
                turn_behavior="forced_retreat",
            ),
            allows_higher_slots=True,
            target_count=1,
            target_count_per_slot_above=1,
            animation="command",
        )
    except Exception:
        logger.exception("Failed to build 2024 Command.")
        raise


def suggestion_2024(save_dc: int) -> SpellSaveAction:
    """2024 Suggestion: seen hearing creature, Wisdom save, Charmed, stop fighting."""
    try:
        return SpellSaveAction(
            id="suggestion",
            name="Suggestion",
            level=2,
            action_cost="action",
            range_ft=30,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            requires_target_hearing=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed",
                duration_rounds=4800,
                expiry_timing="source_turn_end",
                turn_behavior="forced_retreat",
                ends_on_damage=True,
            ),
            concentration=True,
            duration_minutes=480,
            allows_higher_slots=True,
            animation="suggestion",
        )
    except Exception:
        logger.exception("Failed to build 2024 Suggestion.")
        raise


def geas_2024(save_dc: int) -> SpellSaveAction:
    """2024 Geas: 1-minute cast, Wisdom save, Charmed until ended by listed spells."""
    try:
        return SpellSaveAction(
            id="geas",
            name="Geas",
            level=5,
            action_cost="action",
            range_ft=60,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed",
                expiry_timing="source_turn_end",
            ),
            allows_higher_slots=True,
            cast_rounds=10,
            animation="geas",
        )
    except Exception:
        logger.exception("Failed to build 2024 Geas.")
        raise
