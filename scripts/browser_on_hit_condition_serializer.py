from __future__ import annotations

import logging
from typing import Any

from app.domain.weapons import OnHitConditionSave

logger = logging.getLogger(__name__)


def _value(item: Any) -> Any:
    try:
        return getattr(item, "value", item)
    except Exception:
        logger.exception("Failed to serialize enum-like browser value.")
        raise


def serialize_on_hit_condition_save(effect: OnHitConditionSave) -> dict[str, Any]:
    """Serialize one source-neutral on-hit condition rider for the browser."""
    try:
        row: dict[str, Any] = {
            "saveAbility": _value(effect.save_ability),
            "dc": effect.dc,
            "conditionId": effect.condition_id,
            "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
        }
        if effect.duration_rounds is not None:
            row["durationRounds"] = effect.duration_rounds
        if effect.repeat_save_timing is not None:
            row["repeatSaveTiming"] = _value(effect.repeat_save_timing)
        if effect.repeat_save_failure_condition_id:
            row["repeatSaveFailureConditionId"] = effect.repeat_save_failure_condition_id
        if effect.failure_margin_escalation:
            escalation = effect.failure_margin_escalation
            row["failureMarginEscalation"] = {
                "margin": escalation.margin,
                "additionalConditionIds": list(escalation.additional_condition_ids),
                "replacementDurationDiceCount": escalation.replacement_duration_dice_count,
                "replacementDurationDiceSize": escalation.replacement_duration_dice_size,
                "replacementDurationRoundMultiplier": escalation.replacement_duration_round_multiplier,
                "endsOnDamage": escalation.ends_on_damage,
                "allowedRemovalActionIds": list(escalation.allowed_removal_action_ids),
            }
        if effect.failure_push_ft:
            row["failurePushFt"] = effect.failure_push_ft
        if effect.excluded_creature_types:
            row["excludedCreatureTypes"] = list(effect.excluded_creature_types)
        if effect.excluded_creature_subtypes:
            row["excludedCreatureSubtypes"] = list(effect.excluded_creature_subtypes)
        if effect.cannot_regain_hit_points:
            row["cannotRegainHitPoints"] = True
        if effect.start_of_turn_damage_dice_count:
            row["startOfTurnDamageDiceCount"] = effect.start_of_turn_damage_dice_count
            row["startOfTurnDamageDiceSize"] = effect.start_of_turn_damage_dice_size
            row["startOfTurnDamageType"] = _value(effect.start_of_turn_damage_type)
        return row
    except Exception:
        logger.exception("Failed to serialize on-hit condition save.")
        raise
