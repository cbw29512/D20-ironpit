from __future__ import annotations

import logging
from typing import Any

from browser_attack_effect_serializer import value

logger = logging.getLogger(__name__)


def area_row(area: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"shape": area.shape, "origin": area.origin}
        if area.radius_ft is not None: row["radiusFt"] = area.radius_ft
        if area.length_ft is not None: row["lengthFt"] = area.length_ft
        if area.width_ft is not None: row["widthFt"] = area.width_ft
        return row
    except Exception:
        logger.exception("Failed to serialize universal area targeting.")
        raise


def failure_effect_row(effect: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"kind": effect.kind}
        maximum = getattr(effect, "max_target_size", None)
        if maximum is not None: row["maxTargetSize"] = value(maximum)
        if effect.kind == "grapple":
            row["escapeDc"] = effect.escape_dc
            if effect.restrains: row["restrains"] = True
        elif effect.kind == "condition":
            row["condition"] = effect.condition
            if effect.linked_conditions: row["linkedConditions"] = list(effect.linked_conditions)
            if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
            if effect.expiry_timing: row["expiryTiming"] = effect.expiry_timing
            if effect.duration_rounds is not None: row["durationRounds"] = effect.duration_rounds
            if effect.ends_on_damage: row["endsOnDamage"] = True
            if effect.repeat_save_ability:
                row.update(repeatSaveAbility=effect.repeat_save_ability, repeatSaveDc=effect.repeat_save_dc,
                           repeatSaveTiming=effect.repeat_save_timing)
            if effect.repeat_save_delay_rounds: row["repeatSaveDelayRounds"] = effect.repeat_save_delay_rounds
            if effect.repeat_save_failure_condition:
                row["repeatSaveFailureCondition"] = effect.repeat_save_failure_condition
                if not effect.repeat_save_failure_continues: row["repeatSaveFailureContinues"] = False
                if effect.repeat_save_failure_duration_rounds is not None:
                    row["repeatSaveFailureDurationRounds"] = effect.repeat_save_failure_duration_rounds
                if effect.repeat_save_failure_ends_on_damage: row["repeatSaveFailureEndsOnDamage"] = True
                if effect.repeat_save_failure_allowed_removal_action_ids:
                    row["repeatSaveFailureAllowedRemovalActionIds"] = list(effect.repeat_save_failure_allowed_removal_action_ids)
            if effect.automatic_success_after_rounds is not None:
                row["automaticSuccessAfterRounds"] = effect.automatic_success_after_rounds
            if effect.allowed_removal_action_ids: row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
            if effect.periodic_damage:
                periodic = effect.periodic_damage
                row["periodicDamage"] = {"timing": periodic.timing, "diceCount": periodic.dice_count,
                    "diceSize": periodic.dice_size, "damageBonus": periodic.damage_bonus, "damageType": value(periodic.damage_type)}
        elif effect.kind == "turn-restriction":
            row.update(actionOrBonusOnly=effect.action_or_bonus_only, reactionsDisabled=effect.reactions_disabled,
                       expiryTiming=effect.expiry_timing)
            if effect.speed_multiplier != 1.0: row["speedMultiplier"] = effect.speed_multiplier
            if effect.requires_condition: row["requiresCondition"] = effect.requires_condition
        elif effect.kind == "timed-penalty":
            row.update(d20DisadvantageAbility=effect.d20_disadvantage_ability,
                       damagePenaltyDiceCount=effect.damage_penalty_dice_count,
                       damagePenaltyDiceSize=effect.damage_penalty_dice_size,
                       repeatSaveAbility=effect.repeat_save_ability, repeatSaveDc=effect.repeat_save_dc,
                       repeatSaveTiming=effect.repeat_save_timing)
            if effect.automatic_success_after_rounds is not None: row["automaticSuccessAfterRounds"] = effect.automatic_success_after_rounds
        elif effect.kind in {"attacks-against-advantage", "speed"}:
            row["flatBonus"] = effect.flat_bonus
            if effect.consume_on_attack_against: row["consumeOnAttackAgainst"] = True
            if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
            if effect.expires_at_end_of_target_turn: row["expiresAtEndOfTargetTurn"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize failed-save effect.")
        raise


def save_row(action: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"id": action.id, "name": action.name, "actionCost": action.action_cost,
            "saveAbility": action.save_ability, "dc": action.dc, "range": action.range_ft,
            "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "successDamage": action.success_damage, "animation": action.animation}
        if action.area is not None: row["area"] = area_row(action.area)
        if action.failure_effects: row["failureEffects"] = [failure_effect_row(effect) for effect in action.failure_effects]
        if action.forbid_target_affected_by_action: row["forbidTargetAffectedByAction"] = True
        if action.resource_id is not None: row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.magical_effect: row["magicalEffect"] = True
        if action.target_max_size: row["targetMaxSize"] = value(action.target_max_size)
        if action.required_target_condition: row["requiredTargetCondition"] = action.required_target_condition
        if action.required_target_grappled_by_self: row["requiredTargetGrappledBySelf"] = True
        if action.push_target_away_ft: row["pushTargetAwayFt"] = action.push_target_away_ft
        if action.push_target_max_size: row["pushTargetMaxSize"] = value(action.push_target_max_size)
        if action.grapple_escape_dc is not None: row["grappleEscapeDc"] = action.grapple_escape_dc
        if action.restrains_while_grappled: row["restrainsWhileGrappled"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize save action %s.", action.id)
        raise


def spell_save_row(action: Any) -> dict[str, Any]:
    try:
        row = {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
            "range": action.range_ft, "saveAbility": action.save_ability, "dc": action.dc,
            "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "successDamage": action.success_damage, "animation": action.animation}
        if action.area is not None: row["area"] = area_row(action.area)
        return row
    except Exception:
        logger.exception("Failed to serialize spell save action %s.", action.id)
        raise


def spell_attack_row(action: Any) -> dict[str, Any]:
    return {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
        "range": action.range_ft, "attackBonus": action.attack_bonus, "damageDiceCount": action.damage_dice_count,
        "damageDiceSize": action.damage_dice_size, "damageBonus": action.damage_bonus,
        "damageType": action.damage_type, "animation": action.animation}


def _spell_modifier_row(effect: Any) -> dict[str, Any]:
    row = {"kind": effect.kind, "flatBonus": effect.flat_bonus, "diceCount": effect.dice_count,
           "diceSize": effect.dice_size, "damageType": effect.damage_type}
    if effect.consume_on_attack_against: row["consumeOnAttackAgainst"] = True
    if effect.expires_after_source_turns is not None: row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
    return row


def defense_row(action: Any) -> dict[str, Any]:
    try:
        row = {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
            "range": action.range_ft, "durationMinutes": action.duration_minutes, "targetPolicy": action.target_policy,
            "targetCount": action.target_count, "temporaryHp": action.temporary_hp,
            "temporaryHpPerSlotAbove": action.temporary_hp_per_slot_above,
            "damageResistances": list(action.damage_resistances),
            "modifierEffects": [_spell_modifier_row(effect) for effect in action.modifier_effects],
            "concentration": action.concentration, "priority": action.priority, "animation": action.animation}
        if action.target_count_per_slot_above: row["targetCountPerSlotAbove"] = action.target_count_per_slot_above
        if action.max_hp_increase: row["maxHpIncrease"] = action.max_hp_increase
        if action.current_hp_increase: row["currentHpIncrease"] = action.current_hp_increase
        if action.resource_id is not None: row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.source: row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize defensive spell action %s.", getattr(action, "id", "<unknown>"))
        raise


def healing_row(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
        "targetMode": action.target_mode, "diceCount": action.dice_count, "diceSize": action.dice_size,
        "healingBonus": action.healing_bonus, "animation": action.animation}
    if action.resource_id is not None: row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
    return row


def removal_row(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
        "targetMode": action.target_mode, "removableConditions": list(action.removable_conditions),
        "maxConditionsPerUse": action.max_conditions_per_use, "resourceCosts": dict(action.resource_costs),
        "resourceCostsPerCondition": dict(action.resource_costs_per_condition),
        "reactionTrigger": action.reaction_trigger, "expendsSpellSlot": action.expends_spell_slot,
        "animation": action.animation}
    if action.requires_source_permission: row["requiresSourcePermission"] = True
    return row
