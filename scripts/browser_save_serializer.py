from __future__ import annotations

import logging
from typing import Any

from browser_attack_effect_serializer import value
from browser_save_failure_serializer import failure_effect_row

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


def _damage_component_row(component: Any) -> dict[str, Any]:
    try:
        return {
            "diceCount": component.dice_count,
            "diceSize": component.dice_size,
            "damageBonus": component.damage_bonus,
            "damageType": value(component.damage_type),
        }
    except Exception:
        logger.exception("Failed to serialize additional save damage component.")
        raise


def save_row(action: Any) -> dict[str, Any]:
    try:
        row: dict[str, Any] = {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "saveAbility": action.save_ability, "dc": action.dc, "range": action.range_ft,
            "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "successDamage": action.success_damage, "animation": action.animation,
        }
        if action.additional_damage_components:
            row["additionalDamageComponents"] = [
                _damage_component_row(component)
                for component in action.additional_damage_components
            ]
        _save_optional_fields(row, action)
        return row
    except Exception:
        logger.exception("Failed to serialize save action %s.", action.id)
        raise


def _save_optional_fields(row: dict[str, Any], action: Any) -> None:
    try:
        if action.area is not None:
            row["area"] = area_row(action.area)
        if action.failure_effects:
            row["failureEffects"] = [failure_effect_row(effect) for effect in action.failure_effects]
        if action.forbid_target_affected_by_action:
            row["forbidTargetAffectedByAction"] = True
        if action.resource_id is not None:
            row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.magical_effect:
            row["magicalEffect"] = True
        if action.target_max_size:
            row["targetMaxSize"] = value(action.target_max_size)
        if action.required_target_condition:
            row["requiredTargetCondition"] = action.required_target_condition
        if action.required_target_grappled_by_self:
            row["requiredTargetGrappledBySelf"] = True
        if action.push_target_away_ft:
            row["pushTargetAwayFt"] = action.push_target_away_ft
        if action.push_target_max_size:
            row["pushTargetMaxSize"] = value(action.push_target_max_size)
        if action.grapple_escape_dc is not None:
            row["grappleEscapeDc"] = action.grapple_escape_dc
        if action.restrains_while_grappled:
            row["restrainsWhileGrappled"] = True
    except Exception:
        logger.exception("Failed to serialize optional save action fields.")
        raise


def spell_save_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "saveAbility": action.save_ability, "dc": action.dc,
            "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "successDamage": action.success_damage, "animation": action.animation,
        }
        if action.area is not None:
            row["area"] = area_row(action.area)
        return row
    except Exception:
        logger.exception("Failed to serialize spell save action %s.", action.id)
        raise
