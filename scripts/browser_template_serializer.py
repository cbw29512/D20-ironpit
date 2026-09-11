from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate
from browser_action_serializer import (
    defense_row,
    healing_row,
    removal_row,
    save_row,
    spell_attack_row,
    spell_save_row,
)
from browser_attack_serializer import attack_row

logger = logging.getLogger(__name__)


def _progression_features(template: CombatantTemplate) -> dict[str, Any]:
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


def _resource_definitions(template: CombatantTemplate) -> dict[str, Any]:
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


def _swallow_row(action: Any) -> dict[str, Any]:
    return {
        "id": action.id,
        "name": action.name,
        "maxTargetSize": action.max_target_size.value,
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


def _aura_row(aura: Any) -> dict[str, Any]:
    return {
        "id": aura.id, "name": aura.name, "radius_ft": aura.radius_ft,
        "damage_dice_count": aura.damage_dice_count, "damage_dice_size": aura.damage_dice_size,
        "damage_bonus": aura.damage_bonus, "damage_type": aura.damage_type.value,
        "disabled_while_incapacitated": aura.disabled_while_incapacitated,
    }


def template_row(template: CombatantTemplate) -> dict[str, Any]:
    try:
        traits = {item.value for item in template.combat_traits}
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        row: dict[str, Any] = {
            "id": template.id, "name": template.name, "archetype": template.archetype,
            "level": template.level, "challenge_rating": template.challenge_rating, "kind": template.kind,
            "size": template.size.value, "armor_class": template.armor_class, "max_hp": template.max_hp,
            "speed_ft": template.speed_ft, "movement_modes": template.movement_modes.model_dump(),
            "initiative_bonus": template.initiative_bonus,
            "saving_throw_bonuses": template.saving_throw_bonuses, "skill_bonuses": template.skill_bonuses,
            "attacks": [attack_row(item, traits) for item in attacks], "primary_attack_id": template.weapon_attack.id,
            "saving_throw_actions": [save_row(item) for item in template.saving_throw_actions],
            "traits": sorted(traits), "resources": {item.id: item.max_uses for item in template.resources},
            "resourceDefinitions": _resource_definitions(template),
            "damage_resistances": [item.value for item in template.damage_resistances],
            "damage_vulnerabilities": [item.value for item in template.damage_vulnerabilities],
            "damage_immunities": [item.value for item in template.damage_immunities],
            "condition_immunities": list(template.condition_immunities),
            "visual": {
                "armor": template.visual.armor, "main_hand": template.visual.main_hand,
                "off_hand": template.visual.off_hand, "body_style": template.visual.body_style,
            },
            "source": template.source, **_progression_features(template),
        }
        if template.forced_movement_actions:
            row["forced_movement_actions"] = [
                {
                    "id": action.id, "name": action.name, "direction": action.direction,
                    "distanceFt": action.distance_ft, "targetMode": action.target_mode,
                    "animation": action.animation,
                }
                for action in template.forced_movement_actions
            ]
        if template.swallow_actions:
            row["swallow_actions"] = [_swallow_row(action) for action in template.swallow_actions]
        if template.end_turn_damage_auras:
            row["end_turn_damage_auras"] = [_aura_row(aura) for aura in template.end_turn_damage_auras]
        if template.kind == "monster":
            row["source_trait_names"] = list(template.source_trait_names)
            row["source_reaction_names"] = list(template.source_reaction_names)
            row["source_bonus_action_names"] = list(template.source_bonus_action_names)
            row["source_limited_use_names"] = list(template.source_limited_use_names)
            row["source_legendary_action_names"] = list(template.source_legendary_action_names)
            row["source_spellcasting_fingerprint"] = template.source_spellcasting_fingerprint
        if template.parry_reaction:
            row["parry_reaction"] = {"ac_bonus": template.parry_reaction.ac_bonus}
        if template.redirect_attack_reaction:
            row["redirect_attack_reaction"] = {
                "ally_range_ft": template.redirect_attack_reaction.ally_range_ft,
                "ally_max_size": template.redirect_attack_reaction.ally_max_size.value,
            }
        if template.spell_save_actions:
            row["spell_save_actions"] = [spell_save_row(item) for item in template.spell_save_actions]
        if template.spell_attack_actions:
            row["spell_attack_actions"] = [spell_attack_row(item) for item in template.spell_attack_actions]
        if template.defensive_spell_actions:
            row["defensive_spell_actions"] = [defense_row(item) for item in template.defensive_spell_actions]
        if template.healing_actions:
            row["healingActions"] = [healing_row(item) for item in template.healing_actions]
        if template.condition_removal_actions:
            row["condition_removal_actions"] = [removal_row(item) for item in template.condition_removal_actions]
        if template.attack_action:
            row["attack_action"] = {
                "id": template.attack_action.id,
                "name": template.attack_action.name,
                "slots": [
                    {
                        "attackIds": slot.attack_ids,
                        "saveActionIds": slot.save_action_ids,
                        "forcedMovementActionIds": slot.forced_movement_action_ids,
                    }
                    for slot in template.attack_action.slots
                ],
            }
        return row
    except Exception:
        logger.exception("Failed to serialize combatant template %s.", template.id)
        raise