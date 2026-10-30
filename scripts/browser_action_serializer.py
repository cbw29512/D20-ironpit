from __future__ import annotations

import logging
from typing import Any

from browser_save_failure_serializer import failure_effect_row
from browser_save_serializer import area_row, save_row, spell_save_row

logger = logging.getLogger(__name__)


def spell_attack_row(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "attackBonus": action.attack_bonus,
            "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus, "damageType": action.damage_type,
            "animation": action.animation,
        }
    except Exception:
        logger.exception("Failed to serialize spell attack action %s.", action.id)
        raise


def _spell_modifier_row(effect: Any) -> dict[str, Any]:
    try:
        row = {
            "kind": effect.kind, "flatBonus": effect.flat_bonus,
            "diceCount": effect.dice_count, "diceSize": effect.dice_size,
            "damageType": effect.damage_type,
        }
        if effect.consume_on_attack_against:
            row["consumeOnAttackAgainst"] = True
        if effect.expires_after_source_turns is not None:
            row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
        return row
    except Exception:
        logger.exception("Failed to serialize spell modifier effect.")
        raise


def defense_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "durationMinutes": action.duration_minutes,
            "targetPolicy": action.target_policy, "targetCount": action.target_count,
            "temporaryHp": action.temporary_hp,
            "temporaryHpPerSlotAbove": action.temporary_hp_per_slot_above,
            "damageResistances": list(action.damage_resistances),
            "modifierEffects": [_spell_modifier_row(effect) for effect in action.modifier_effects],
            "concentration": action.concentration, "priority": action.priority,
            "animation": action.animation,
        }
        if action.target_count_per_slot_above:
            row["targetCountPerSlotAbove"] = action.target_count_per_slot_above
        if action.max_hp_increase:
            row["maxHpIncrease"] = action.max_hp_increase
        if action.current_hp_increase:
            row["currentHpIncrease"] = action.current_hp_increase
        if action.resource_id is not None:
            row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize defensive spell action %s.", getattr(action, "id", "<unknown>"))
        raise


def healing_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "range": action.range_ft, "targetMode": action.target_mode,
            "diceCount": action.dice_count, "diceSize": action.dice_size,
            "healingBonus": action.healing_bonus, "animation": action.animation,
        }
        if action.resource_id is not None:
            row["resourceId"], row["resourceCost"] = action.resource_id, action.resource_cost
        return row
    except Exception:
        logger.exception("Failed to serialize healing action %s.", getattr(action, "id", "<unknown>"))
        raise


def removal_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "range": action.range_ft, "targetMode": action.target_mode,
            "removableConditions": list(action.removable_conditions),
            "maxConditionsPerUse": action.max_conditions_per_use,
            "resourceCosts": dict(action.resource_costs),
            "resourceCostsPerCondition": dict(action.resource_costs_per_condition),
            "reactionTrigger": action.reaction_trigger,
            "expendsSpellSlot": action.expends_spell_slot,
            "animation": action.animation,
        }
        if action.requires_source_permission:
            row["requiresSourcePermission"] = True
        return row
    except Exception:
        logger.exception("Failed to serialize condition removal action %s.", getattr(action, "id", "<unknown>"))
        raise


__all__ = [
    "area_row", "defense_row", "failure_effect_row", "healing_row",
    "removal_row", "save_row", "spell_attack_row", "spell_save_row",
]
