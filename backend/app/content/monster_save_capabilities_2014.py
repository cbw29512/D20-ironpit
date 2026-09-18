from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import ResourceDefinition
from app.domain.recharge import RechargeRule

logger = logging.getLogger(__name__)


def supports_save_action_2014(action: object) -> bool:
    try:
        if not isinstance(action, dict):
            return False
        if not {"id", "name", "save_ability", "dc", "range_ft"} <= set(action):
            return False
        if action.get("failure_control_effect") or action.get("failure_push_ft"):
            return False
        count = int(action.get("damage_dice_count", 0) or 0)
        if count and not action.get("damage_type"):
            return False
        area = action.get("area")
        return area is None or isinstance(area, dict)
    except Exception:
        logger.exception("Failed to classify a 2014 save action.")
        raise


def supports_recharge_rules_2014(monster: SourceMonster2014) -> bool:
    try:
        if monster.rest_recharge_action_ids:
            return False
        supported_ids = {
            str(action.get("id")) for action in monster.saving_throw_actions
            if supports_save_action_2014(action) and isinstance(action, dict)
        }
        return all(action_id in supported_ids for action_id in monster.action_recharges)
    except Exception:
        logger.exception("Failed to classify 2014 Recharge rules for %s.", monster.name)
        raise


def action_label_2014(name: str) -> str:
    return name.split(" (Recharge", 1)[0].strip().casefold()


def save_capabilities_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    try:
        result = []
        for action in monster.saving_throw_actions:
            if not supports_save_action_2014(action):
                continue
            damage = None
            count = int(action.get("damage_dice_count", 0) or 0)
            if count:
                damage = DiceSpec(
                    count=count,
                    size=int(action.get("damage_dice_size", 6)),
                    bonus=int(action.get("damage_bonus", 0) or 0),
                )
            result.append(SaveCapabilityDefinition(
                id=str(action["id"]), name=str(action["name"]),
                save_ability=str(action["save_ability"]), dc=int(action["dc"]),
                range_ft=int(action["range_ft"]), area=action.get("area"),
                damage=damage, damage_type=action.get("damage_type"),
                success_damage=str(action.get("success_damage", "none")),
                resource_id=action.get("resource_id"),
                resource_cost=int(action.get("resource_cost", 1) or 1),
                requires_no_active_grapple=bool(action.get("requires_no_active_grapple", False)),
                magical_effect=bool(action.get("magical_effect", False)),
                animation=str(action.get("animation", "save-effect")),
            ))
        return result
    except Exception:
        logger.exception("Failed to adapt 2014 save actions for %s.", monster.name)
        raise


def save_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    ids = {
        action.resource_id for action in save_capabilities_2014(monster)
        if action.resource_id is not None and action.resource_id in monster.action_recharges
    }
    return [
        ResourceDefinition(id=resource_id, name=resource_id.replace("-", " ").title(), max_uses=1)
        for resource_id in sorted(ids)
    ]


def recharge_rules_2014(monster: SourceMonster2014) -> list[RechargeRule]:
    return [
        RechargeRule(resource_id=action_id, minimum_roll=minimum)
        for action_id, minimum in sorted(monster.action_recharges.items())
    ] if supports_recharge_rules_2014(monster) else []
