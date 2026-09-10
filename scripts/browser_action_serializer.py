from __future__ import annotations

import logging
from typing import Any

from browser_attack_effect_serializer import value

logger = logging.getLogger(__name__)


def area_row(area: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {"shape": area.shape, "origin": area.origin}
        if area.radius_ft is not None:
            row["radiusFt"] = area.radius_ft
        if area.length_ft is not None:
            row["lengthFt"] = area.length_ft
        if area.width_ft is not None:
            row["widthFt"] = area.width_ft
        return row
    except Exception:
        logger.exception("Failed to serialize universal area targeting.")
        raise


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
        elif effect.kind == "condition":
            row["condition"] = effect.condition
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
        elif effect.kind == "turn-restriction":
            row["actionOrBonusOnly"] = effect.action_or_bonus_only
            row["reactionsDisabled"] = effect.reactions_disabled
            row["expiryTiming"] = effect.expiry_timing
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


def save_row(action: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {
            "id": action.id, "name": action.name, "saveAbility": action.save_ability, "dc": action.dc,
            "range": action.range_ft, "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size, "damageBonus": action.damage_bonus,
            "damageType": action.damage_type, "successDamage": action.success_damage, "animation": action.animation,
        }
        if action.area is not None:
            row["area"] = area_row(action.area)
        if action.failure_effects:
            row["failureEffects"] = [failure_effect_row(effect) for effect in action.failure_effects]
        if action.resource_id is not None:
            row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.target_max_size:
            row["targetMaxSize"] = value(action.target_max_size)
        if action.grapple_escape_dc is not None:
            row["grappleEscapeDc"] = action.grapple_escape_dc
        if action.restrains_while_grappled:
            row["restrainsWhileGrappled"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize save action %s.", action.id)
        raise


def spell_save_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
            "range": action.range_ft, "saveAbility": action.save_ability, "dc": action.dc,
            "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "successDamage": action.success_damage, "upcastDicePerLevel": action.upcast_dice_per_level,
            "concentration": action.concentration, "animation": action.animation,
        }
        if action.area_radius_ft is not None:
            row["areaRadius"] = action.area_radius_ft
        return row
    except Exception:
        logger.exception("Failed to serialize spell-save action %s.", action.id)
        raise


def modifier_effect_row(effect: Any) -> dict[str, Any]:
    try:
        row = {
            "kind": effect.kind, "flatBonus": effect.flat_bonus, "diceCount": effect.dice_count,
            "diceSize": effect.dice_size, "damageType": effect.damage_type,
        }
        if effect.consume_on_attack_against:
            row["consumeOnAttackAgainst"] = True
        if effect.expires_after_source_turns is not None:
            row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
        return row
    except Exception:
        logger.exception("Failed to serialize modifier effect.")
        raise


def spell_attack_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
            "range": action.range_ft, "attackBonus": action.attack_bonus,
            "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "onHitModifierEffects": [modifier_effect_row(effect) for effect in action.on_hit_modifier_effects],
            "animation": action.animation,
        }
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize spell-attack action %s.", action.id)
        raise


def healing_row(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "range": action.range_ft, "targetMode": action.target_mode,
            "diceCount": action.dice_count, "diceSize": action.dice_size,
            "healingBonus": action.healing_bonus, "resourceId": action.resource_id,
            "resourceCost": action.resource_cost, "animation": action.animation,
        }
    except Exception:
        logger.exception("Failed to serialize healing action %s.", action.id)
        raise


def defense_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
            "range": action.range_ft, "durationMinutes": action.duration_minutes,
            "targetPolicy": action.target_policy, "targetCount": action.target_count,
            "temporaryHp": action.temporary_hp, "temporaryHpPerSlotAbove": action.temporary_hp_per_slot_above,
            "damageResistances": list(action.damage_resistances),
            "modifierEffects": [modifier_effect_row(effect) for effect in action.modifier_effects],
            "concentration": action.concentration, "priority": action.priority, "animation": action.animation,
        }
        if action.max_hp_increase:
            row["maxHpIncrease"] = action.max_hp_increase
        if action.current_hp_increase:
            row["currentHpIncrease"] = action.current_hp_increase
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize defensive action %s.", action.id)
        raise


def removal_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
            "targetMode": action.target_mode, "removableConditions": list(action.removable_conditions),
            "maxConditionsPerUse": action.max_conditions_per_use, "resourceCosts": dict(action.resource_costs),
            "resourceCostsPerCondition": dict(action.resource_costs_per_condition),
            "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
        }
        if action.reaction_trigger:
            row["reactionTrigger"] = action.reaction_trigger
        return row
    except Exception:
        logger.exception("Failed to serialize condition-removal action %s.", action.id)
        raise
