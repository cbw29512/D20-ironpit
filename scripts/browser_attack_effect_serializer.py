from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def value(item: Any) -> Any:
    try:
        return getattr(item, "value", item)
    except Exception:
        logger.exception("Failed to normalize browser serializer value %r.", item)
        raise


def control_row(effect: Any) -> dict[str, Any] | None:
    try:
        if effect is None:
            return None
        row: dict[str, Any] = {}
        if effect.max_target_size:
            row["maxTargetSize"] = value(effect.max_target_size)
        if effect.grapple_escape_dc is not None:
            row["grappleEscapeDc"] = effect.grapple_escape_dc
        if effect.restrains_while_grappled:
            row["restrainsWhileGrappled"] = True
        if effect.conditions_while_grappled:
            row["conditionsWhileGrappled"] = list(effect.conditions_while_grappled)
        if effect.condition_id:
            row["conditionId"] = effect.condition_id
            if effect.expires_at_start_of_source_turn:
                row["expiresAtStartOfSourceTurn"] = True
            if effect.expiry_timing:
                row["expiryTiming"] = effect.expiry_timing
            if effect.repeat_save_ability:
                row["repeatSaveAbility"] = effect.repeat_save_ability
                row["repeatSaveDc"] = effect.repeat_save_dc
                row["repeatSaveTiming"] = effect.repeat_save_timing
                if effect.repeat_save_delay_rounds:
                    row["repeatSaveDelayRounds"] = effect.repeat_save_delay_rounds
            if effect.allowed_removal_action_ids:
                row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
        return row or None
    except Exception:
        logger.exception("Failed to serialize browser control effect.")
        raise


def hit_modifier_row(effect: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"kind": effect.kind}
        if effect.flat_bonus:
            row["flatBonus"] = effect.flat_bonus
        if effect.consume_on_attack_against:
            row["consumeOnAttackAgainst"] = True
        if effect.expires_at_start_of_source_turn:
            row["expiresAtStartOfSourceTurn"] = True
        if effect.expires_at_end_of_target_turn:
            row["expiresAtEndOfTargetTurn"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize browser hit modifier.")
        raise


def charge_row(profile: Any) -> dict[str, Any] | None:
    try:
        if profile is None:
            return None
        row: dict[str, Any] = {"minimumMove": profile.minimum_move_ft}
        if profile.prone_max_target_size is not None:
            row["proneMaxSize"] = value(profile.prone_max_target_size)
        if profile.max_target_size is not None and profile.max_target_size != profile.prone_max_target_size:
            row["targetMaxSize"] = value(profile.max_target_size)
        if profile.bonus_damage is not None:
            row.update(
                diceCount=profile.bonus_damage.dice_count,
                diceSize=profile.bonus_damage.dice_size,
                damageType=value(profile.bonus_damage.damage_type),
            )
        if profile.replacement_damage is not None:
            replacement = profile.replacement_damage
            row["replacementDamage"] = {
                "diceCount": replacement.dice_count,
                "diceSize": replacement.dice_size,
                "damageBonus": replacement.damage_bonus,
                "damageType": value(replacement.damage_type),
            }
        if profile.follow_up_attack_id:
            row["followUpAttackId"] = profile.follow_up_attack_id
        return row
    except Exception:
        logger.exception("Failed to serialize browser charge profile.")
        raise
