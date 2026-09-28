from __future__ import annotations

from app.domain.actions import SavingThrowAction
from app.domain.combatants import ResourceDefinition
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting


def intimidating_presence_resource(level: int) -> ResourceDefinition | None:
    try:
        if level < 14:
            return None
        return ResourceDefinition(
            id="intimidating-presence",
            name="Intimidating Presence",
            max_uses=1,
        )
    except Exception:
        raise


def intimidating_presence_action(strength: int, proficiency_bonus: int) -> SavingThrowAction:
    try:
        dc = 8 + ((strength - 10) // 2) + proficiency_bonus
        return SavingThrowAction(
            id="intimidating-presence",
            name="Intimidating Presence",
            action_cost="bonus_action",
            save_ability="wisdom",
            dc=dc,
            range_ft=0,
            area=AreaTargeting(shape="emanation", origin="self", radius_ft=30),
            resource_id="intimidating-presence",
            effect_tags=["frightened"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened",
                duration_rounds=10,
                expiry_timing="source_turn_start",
                repeat_save_ability="wisdom",
                repeat_save_dc=dc,
                repeat_save_timing="target_turn_end",
            ),
            animation="condition",
        )
    except Exception:
        raise


def intimidating_presence_resource_conversions(
    features: tuple[str, ...],
) -> list[ResourceConversionAction]:
    try:
        if "intimidating-presence" not in features:
            return []
        return [
            ResourceConversionAction(
                id="restore-intimidating-presence",
                name="Intimidating Presence",
                action_cost="none",
                source_resource_id="rage",
                source_cost=1,
                target_resource_id="intimidating-presence",
                target_gain=1,
                priority=50,
                source="D&D Beyond Basic Rules 2024: Berserker Intimidating Presence",
            )
        ]
    except Exception:
        raise
