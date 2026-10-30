from __future__ import annotations

import logging
from typing import Any

from browser_attack_effect_serializer import value

logger = logging.getLogger(__name__)


def failure_effect_row(effect: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"kind": effect.kind}
        maximum = getattr(effect, "max_target_size", None)
        if maximum is not None:
            row["maxTargetSize"] = value(maximum)
        if effect.kind == "grapple":
            row["escapeDc"] = effect.escape_dc
            if effect.restrains:
                row["restrains"] = True
            if effect.linked_conditions:
                row["linkedConditions"] = list(effect.linked_conditions)
            if effect.periodic_damage is not None:
                periodic = effect.periodic_damage
                row["periodicDamage"] = {
                    "timing": periodic.timing,
                    "diceCount": periodic.dice_count,
                    "diceSize": periodic.dice_size,
                    "damageBonus": periodic.damage_bonus,
                    "damageType": value(periodic.damage_type),
                }
        elif effect.kind == "condition":
            _condition_fields(row, effect)
        elif effect.kind == "turn-restriction":
            row.update(
                actionOrBonusOnly=effect.action_or_bonus_only,
                reactionsDisabled=effect.reactions_disabled,
                expiryTiming=effect.expiry_timing,
            )
            if effect.speed_multiplier != 1.0:
                row["speedMultiplier"] = effect.speed_multiplier
            if effect.requires_condition:
                row["requiresCondition"] = effect.requires_condition
        elif effect.kind == "timed-penalty":
            row.update(
                d20DisadvantageAbility=effect.d20_disadvantage_ability,
                damagePenaltyDiceCount=effect.damage_penalty_dice_count,
                damagePenaltyDiceSize=effect.damage_penalty_dice_size,
                repeatSaveAbility=effect.repeat_save_ability,
                repeatSaveDc=effect.repeat_save_dc,
                repeatSaveTiming=effect.repeat_save_timing,
            )
            if effect.automatic_success_after_rounds is not None:
                row["automaticSuccessAfterRounds"] = effect.automatic_success_after_rounds
        elif effect.kind == "zero-hp-replacement":
            row.update(effectId=effect.effect_id, replacementMode=effect.replacement_mode,
                       controlMode=effect.control_mode, replacementHp=effect.replacement_hp)
        elif effect.kind in {"attacks-against-advantage", "speed"}:
            row["flatBonus"] = effect.flat_bonus
            if effect.consume_on_attack_against:
                row["consumeOnAttackAgainst"] = True
            if effect.expires_at_start_of_source_turn:
                row["expiresAtStartOfSourceTurn"] = True
            if effect.expires_at_end_of_target_turn:
                row["expiresAtEndOfTargetTurn"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize failed-save effect.")
        raise


def _condition_fields(row: dict[str, Any], effect: Any) -> None:
    try:
        row["condition"] = effect.condition
        if effect.linked_conditions:
            row["linkedConditions"] = list(effect.linked_conditions)
        if effect.expires_at_start_of_source_turn:
            row["expiresAtStartOfSourceTurn"] = True
        if effect.expiry_timing:
            row["expiryTiming"] = effect.expiry_timing
        if effect.duration_rounds is not None:
            row["durationRounds"] = effect.duration_rounds
        if effect.ends_on_damage:
            row["endsOnDamage"] = True
        if effect.repeat_save_ability:
            row.update(
                repeatSaveAbility=effect.repeat_save_ability,
                repeatSaveDc=effect.repeat_save_dc,
                repeatSaveTiming=effect.repeat_save_timing,
            )
        if effect.repeat_save_delay_rounds:
            row["repeatSaveDelayRounds"] = effect.repeat_save_delay_rounds
        if effect.repeat_save_failure_condition:
            row["repeatSaveFailureCondition"] = effect.repeat_save_failure_condition
            if not effect.repeat_save_failure_continues:
                row["repeatSaveFailureContinues"] = False
            if effect.repeat_save_failure_duration_rounds is not None:
                row["repeatSaveFailureDurationRounds"] = effect.repeat_save_failure_duration_rounds
            if effect.repeat_save_failure_ends_on_damage:
                row["repeatSaveFailureEndsOnDamage"] = True
            if effect.repeat_save_failure_allowed_removal_action_ids:
                row["repeatSaveFailureAllowedRemovalActionIds"] = list(
                    effect.repeat_save_failure_allowed_removal_action_ids
                )
        if effect.automatic_success_after_rounds is not None:
            row["automaticSuccessAfterRounds"] = effect.automatic_success_after_rounds
        if effect.allowed_removal_action_ids:
            row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
        if effect.periodic_damage:
            periodic = effect.periodic_damage
            row["periodicDamage"] = {
                "timing": periodic.timing,
                "diceCount": periodic.dice_count,
                "diceSize": periodic.dice_size,
                "damageBonus": periodic.damage_bonus,
                "damageType": value(periodic.damage_type),
            }
    except Exception:
        logger.exception("Failed to serialize failed-save condition fields.")
        raise
