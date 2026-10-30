from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def progression_features(template: CombatantTemplate) -> dict[str, Any]:
    try:
        features = template.progression_features
        row: dict[str, Any] = {}
        if features.critical_hit_minimum != 20:
            row["critical_hit_minimum"] = features.critical_hit_minimum
        if features.initiative_advantage:
            row["initiative_advantage"] = True
        if features.athletics_advantage:
            row["athletics_advantage"] = True
        if features.critical_move_fraction:
            row["critical_move_fraction"] = features.critical_move_fraction
        return row
    except Exception:
        logger.exception("Failed to serialize progression features for %s.", template.id)
        raise


def resource_definitions(template: CombatantTemplate) -> dict[str, Any]:
    try:
        rows: dict[str, Any] = {}
        for resource in template.resources:
            row: dict[str, Any] = {"name": resource.name, "maxUses": resource.max_uses}
            if resource.recharge is not None:
                row["recharge"] = {
                    "trigger": resource.recharge.trigger,
                    "dieSize": resource.recharge.die_size,
                    "minimumRoll": resource.recharge.minimum_roll,
                }
            rows[resource.id] = row
        return rows
    except Exception:
        logger.exception("Failed to serialize resource definitions for %s.", template.id)
        raise


def legendary_action_row(template: CombatantTemplate) -> dict[str, Any] | None:
    try:
        pool = template.legendary_actions
        if pool is None:
            return None
        return {
            "max_uses": pool.max_uses,
            "options": [
                {
                    "id": option.id,
                    "name": option.name,
                    "kind": option.kind,
                    "action_id": option.action_id,
                    "cost": option.cost,
                    "once_until_owner_turn": option.once_until_owner_turn,
                }
                for option in pool.options
            ],
        }
    except Exception:
        logger.exception("Failed to serialize legendary actions for %s.", template.id)
        raise


def automatic_spell_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "applications": action.applications,
            "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "allowSplitTargets": action.allow_split_targets,
            "animation": action.animation,
        }
        if action.applications_per_slot_above:
            row["applicationsPerSlotAbove"] = action.applications_per_slot_above
        if action.resource_id is not None:
            row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize automatic spell action %s.", getattr(action, "id", "<unknown>"))
        raise
