from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def failed_save_timed_effect_row(rider: Any) -> dict[str, Any]:
    try:
        row = {
            "effectId": rider.effect_id,
            "durationRounds": rider.duration_rounds,
            "expiryTiming": rider.expiry_timing,
            "repeatSaveAbility": rider.repeat_save_ability,
            "repeatSaveDc": rider.repeat_save_dc,
            "repeatSaveTiming": rider.repeat_save_timing,
            "turnBehavior": rider.turn_behavior,
            "endsOnDamage": rider.ends_on_damage,
            "endsIfSourceIncapacitated": rider.ends_if_source_incapacitated,
            "endsIfSourceDead": rider.ends_if_source_dead,
            "nextAttackDisadvantage": rider.next_attack_disadvantage,
            "repeatSaveFailuresToLock": rider.repeat_save_failures_to_lock,
        }
        if rider.additional_effect_ids:
            row["additionalEffectIds"] = list(rider.additional_effect_ids)
        if rider.failure_margin_escalation is not None:
            escalation = rider.failure_margin_escalation
            row["failureMarginEscalation"] = {
                "margin": escalation.margin,
                "additionalConditionIds": list(escalation.additional_condition_ids),
            }
        if rider.damage_repeat_save_trigger != "none":
            row["damageRepeatSaveTrigger"] = rider.damage_repeat_save_trigger
        if rider.repeat_save_before_damaging_terrain:
            row["repeatSaveBeforeDamagingTerrain"] = True
        if rider.source_maintenance_action_cost != "none":
            row["sourceMaintenanceActionCost"] = rider.source_maintenance_action_cost
        if rider.repeat_save_failure_condition_id:
            row["repeatSaveFailureConditionId"] = rider.repeat_save_failure_condition_id
        if rider.allowed_removal_action_ids:
            row["allowedRemovalActionIds"] = list(rider.allowed_removal_action_ids)
        if rider.escape_check_ability:
            row["escapeCheckAbility"] = rider.escape_check_ability
            row["escapeCheckDc"] = rider.escape_check_dc
        if rider.source_effect_immunity_on_end:
            row["sourceEffectImmunityOnEnd"] = True
        if rider.repeat_save_disadvantage_while_source_visible:
            row["repeatSaveDisadvantageWhileSourceVisible"] = True
        if rider.start_of_turn_damage_dice_count:
            row["startOfTurnDamageDiceCount"] = rider.start_of_turn_damage_dice_count
            row["startOfTurnDamageDiceSize"] = rider.start_of_turn_damage_dice_size
            row["startOfTurnDamageType"] = rider.start_of_turn_damage_type.value
        return row
    except Exception:
        logger.exception("Failed to serialize failed-save timed rider %s.", getattr(rider, "effect_id", "?"))
        raise
