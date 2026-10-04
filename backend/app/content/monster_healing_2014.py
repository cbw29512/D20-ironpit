from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition
from app.domain.healing_actions import HealingAction

logger = logging.getLogger(__name__)


def healing_actions_2014(monster: SourceMonster2014) -> list[HealingAction]:
    try:
        actions: list[HealingAction] = []
        for raw in monster.healing_actions:
            if not isinstance(raw, dict):
                raise ValueError(f"{monster.name} healing action is not structured.")
            actions.append(HealingAction(
                id=str(raw["id"]),
                name=str(raw["name"]),
                action_cost=str(raw.get("action_cost") or "action"),
                range_ft=int(raw.get("range_ft") or 5),
                target_mode=str(raw.get("target_mode") or "self_or_ally"),
                dice_count=int(raw.get("dice_count") or 0),
                dice_size=int(raw.get("dice_size") or 8),
                healing_bonus=int(raw.get("healing_bonus") or 0),
                removable_conditions=list(raw.get("removable_conditions") or []),
                resource_id=raw.get("resource_id"),
                resource_cost=int(raw.get("resource_cost") or 1),
                animation=str(raw.get("animation") or "healing"),
            ))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 healing actions for %s.", monster.name)
        raise


def healing_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    try:
        resources: list[ResourceDefinition] = []
        for action in healing_actions_2014(monster):
            if not action.resource_id:
                continue
            uses = int(monster.limited_action_uses.get(action.resource_id, 0) or 0)
            if uses <= 0:
                raise ValueError(f"{monster.name} healing action {action.id} lacks a use count.")
            resources.append(ResourceDefinition(
                id=action.resource_id,
                name=action.name,
                max_uses=uses,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile 2014 healing resources for %s.", monster.name)
        raise


def supports_healing_2014(monster: SourceMonster2014) -> bool:
    try:
        if not monster.healing_actions:
            return True
        return bool(healing_actions_2014(monster)) and bool(healing_resources_2014(monster))
    except Exception:
        logger.exception("Failed to classify 2014 healing support for %s.", monster.name)
        raise


def healing_action_names_2014(monster: SourceMonster2014) -> set[str]:
    return {action.name.casefold() for action in healing_actions_2014(monster)}
