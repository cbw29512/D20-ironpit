from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def swallow_row(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name,
            "maxTargetSize": action.max_target_size.value,
            "actionCost": action.action_cost,
            "maxSwallowedTargets": action.max_swallowed_targets,
            "requiresGrappledTarget": action.requires_grappled_target,
            "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size,
            "damageBonus": action.damage_bonus,
            "damageType": action.damage_type.value,
            "firstTickDelayRounds": action.first_tick_delay_rounds,
            "tickTiming": action.tick_timing,
            "disgorgeAfterFirstTick": action.disgorge_after_first_tick,
            "appliesBlinded": action.applies_blinded,
            "appliesRestrained": action.applies_restrained,
            "totalCoverFromOutside": action.total_cover_from_outside,
            "forbiddenAttackIdsWhileActive": list(action.forbidden_attack_ids_while_active),
        }
    except Exception:
        logger.exception("Failed to serialize Swallow action %s.", getattr(action, "id", "<unknown>"))
        raise


def aura_row(aura: Any) -> dict[str, Any]:
    try:
        return {
            "id": aura.id, "name": aura.name, "radius_ft": aura.radius_ft,
            "damage_dice_count": aura.damage_dice_count,
            "damage_dice_size": aura.damage_dice_size,
            "damage_bonus": aura.damage_bonus,
            "damage_type": aura.damage_type.value,
            "disabled_while_incapacitated": aura.disabled_while_incapacitated,
            "applies_burning": aura.applies_burning,
        }
    except Exception:
        logger.exception("Failed to serialize damage aura %s.", getattr(aura, "id", "<unknown>"))
        raise


def grapple_contact_row(effect: Any) -> dict[str, Any]:
    try:
        return {
            "id": effect.id, "name": effect.name,
            "damage_dice_count": effect.damage_dice_count,
            "damage_dice_size": effect.damage_dice_size,
            "damage_bonus": effect.damage_bonus,
            "damage_type": effect.damage_type.value,
        }
    except Exception:
        logger.exception("Failed to serialize grapple-contact damage %s.", getattr(effect, "id", "<unknown>"))
        raise


def start_turn_aura_row(aura: Any) -> dict[str, Any]:
    try:
        return {
            "id": aura.id, "name": aura.name, "radius_ft": aura.radius_ft,
            "save_ability": aura.save_ability, "dc": aura.dc,
            "condition": aura.condition, "expiry_timing": aura.expiry_timing,
            "magical_effect": aura.magical_effect,
            "disabled_while_incapacitated": aura.disabled_while_incapacitated,
            "success_grants_source_immunity": aura.success_grants_source_immunity,
            "requires_source_reaction": aura.requires_source_reaction,
        }
    except Exception:
        logger.exception("Failed to serialize start-turn aura %s.", getattr(aura, "id", "<unknown>"))
        raise


def roll_advantage_aura_row(aura: Any) -> dict[str, Any]:
    try:
        return {
            "id": aura.id, "name": aura.name, "radius_ft": aura.radius_ft,
            "target_scope": aura.target_scope,
            "attack_roll_advantage": aura.attack_roll_advantage,
            "saving_throw_advantage": aura.saving_throw_advantage,
            "disabled_while_incapacitated": aura.disabled_while_incapacitated,
        }
    except Exception:
        logger.exception("Failed to serialize roll-advantage aura %s.", getattr(aura, "id", "<unknown>"))
        raise


def regeneration_row(rule: Any) -> dict[str, Any]:
    try:
        return {
            "hitPoints": rule.hit_points,
            "suppressedByDamageTypes": [item.value for item in rule.suppressed_by_damage_types],
            "diesAtStartTurnIfZeroAndSuppressed": rule.dies_at_start_turn_if_zero_and_suppressed,
        }
    except Exception:
        logger.exception("Failed to serialize regeneration rule.")
        raise


def death_trigger_row(effect: Any) -> dict[str, Any]:
    try:
        row = {
            "id": effect.id, "name": effect.name, "radius_ft": effect.radius_ft,
            "save_ability": effect.save_ability, "dc": effect.dc,
            "damage_dice_count": effect.damage_dice_count,
            "damage_dice_size": effect.damage_dice_size,
            "damage_bonus": effect.damage_bonus,
            "damage_type": effect.damage_type.value,
            "half_damage_on_success": effect.half_damage_on_success,
        }
        if effect.additional_damage_components:
            row["additional_damage_components"] = [
                {
                    "dice_count": part.dice_count,
                    "dice_size": part.dice_size,
                    "damage_bonus": part.damage_bonus,
                    "damage_type": part.damage_type.value,
                }
                for part in effect.additional_damage_components
            ]
        return row
    except Exception:
        logger.exception("Failed to serialize death-trigger effect %s.", getattr(effect, "id", "<unknown>"))
        raise
