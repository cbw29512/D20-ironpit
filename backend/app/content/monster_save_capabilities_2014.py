from __future__ import annotations

import logging

from app.content.monster_arena_action_policy_2014 import action_label_2014, arena_unavailable_recharge_ids_2014
from app.content.monster_save_control_2014 import (
    compile_failed_save_control_2014,
    supports_failed_save_control_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_save_outcome_bindings_2014 import source_proven_asymmetric_saves_2014
from app.content.monster_source_visual_save_bindings_2014 import source_proven_visual_saves_2014
from app.content.monster_source_conditioned_save_2014 import source_proven_conditioned_saves_2014
from app.content.monster_source_opening_area_saves_2014 import source_proven_opening_area_saves_2014
from app.content.monster_recharge_self_buffs_2014 import recharge_self_buff_bindings_2014
from app.content.monster_audible_maintained_control_2014 import source_proven_audible_maintained_controls_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_damage import SaveDamageComponent
from app.domain.combatants import ResourceDefinition
from app.domain.recharge import RechargeRule

logger = logging.getLogger(__name__)


def supports_save_action_2014(action: object) -> bool:
    try:
        if not isinstance(action, dict):
            return False
        if not {"id", "name", "save_ability", "dc", "range_ft"} <= set(action):
            return False
        push_ft = action.get("failure_push_ft", 0)
        if (
            isinstance(push_ft, bool)
            or not isinstance(push_ft, int)
            or push_ft < 0
        ):
            return False
        if not supports_failed_save_control_2014(action):
            return False
        count = int(action.get("damage_dice_count", 0) or 0)
        if count and not action.get("damage_type"):
            return False
        components = action.get("damage_components", [])
        if not isinstance(components, list):
            return False
        if components:
            if count or action.get("damage_type") is not None:
                return False
            try:
                for component in components:
                    SaveDamageComponent.model_validate(component)
            except ValueError:
                return False
        choices = action.get("save_ability_choices", [])
        if not isinstance(choices, list):
            return False
        if choices and (
            len(choices) < 2 or
            len(set(choices)) != len(choices) or
            action.get("save_ability") not in choices or
            any(ability not in ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma") for ability in choices)
        ):
            return False
        target_cap = action.get("max_targets", 1)
        if type(target_cap) is not int or not 1 <= target_cap <= 20:
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
        supported = [
            action for action in monster.saving_throw_actions
            if supports_save_action_2014(action) and isinstance(action, dict)
        ]
        supported_ids = {str(action.get("id")) for action in supported}
        supported_resources = {
            str(action.get("resource_id")) for action in supported if action.get("resource_id")
        }
        self_buffs = recharge_self_buff_bindings_2014(monster)
        supported_ids.update(item.action.id for item in self_buffs)
        supported_resources.update(
            item.action.resource_id for item in self_buffs if item.action.resource_id
        )
        excluded_ids = arena_unavailable_recharge_ids_2014(monster)
        return all(
            action_id in supported_ids or action_id in supported_resources or action_id in excluded_ids
            for action_id in monster.action_recharges
        )
    except Exception:
        logger.exception("Failed to classify 2014 Recharge rules for %s.", monster.name)
        raise




def unsupported_save_actions_2014(monster: SourceMonster2014) -> list[object]:
    return [
        action for action in monster.saving_throw_actions
        if not supports_save_action_2014(action)
    ]


def unsupported_source_actions_2014(
    monster: SourceMonster2014, *, recharge_supported: bool | None = None,
) -> list[str]:
    """Reuse an already-checked recharge decision without changing source rules.

    Direct callers can omit it; the helper then checks recharge itself.
    """
    try:
        allowed = {attack.name.casefold() for attack in monster.attacks}
        allowed.update(
            str(action.get("name", "")).casefold()
            for action in monster.saving_throw_actions if isinstance(action, dict)
        )
        allowed.update(item.name.casefold() for item in source_proven_asymmetric_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_visual_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_conditioned_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_opening_area_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_audible_maintained_controls_2014(monster))
        allowed.update(item.action.name.casefold() for item in recharge_self_buff_bindings_2014(monster))
        if monster.multiattack_slots or monster.multiattack_policy is not None or monster.multiattack_binding is not None:
            allowed.add("multiattack")
        if recharge_supported is None:
            recharge_supported = supports_recharge_rules_2014(monster)
        if recharge_supported:
            allowed.add("breath weapons")
        return [name for name in monster.action_names if action_label_2014(name) not in allowed]
    except Exception:
        logger.exception("Failed to classify source actions for %s.", monster.name)
        raise

def save_capabilities_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    try:
        result = []
        for action in monster.saving_throw_actions:
            if not supports_save_action_2014(action) or not isinstance(action, dict):
                continue
            damage = None
            count = int(action.get("damage_dice_count", 0) or 0)
            if count:
                damage = DiceSpec(
                    count=count,
                    size=int(action.get("damage_dice_size", 6)),
                    bonus=int(action.get("damage_bonus", 0) or 0),
                )
            rider = compile_failed_save_control_2014(action)
            effect_tags = {
                str(item).strip().casefold()
                for item in action.get("effect_tags", [])
                if str(item).strip()
            }
            if rider is not None:
                effect_tags.add(rider.effect_id)
            result.append(SaveCapabilityDefinition(
                id=str(action["id"]), name=str(action["name"]),
                save_ability=str(action["save_ability"]), dc=int(action["dc"]),
                range_ft=int(action["range_ft"]), area=action.get("area"),
                max_targets=int(action.get("max_targets", 1)),
                save_ability_choices=list(action.get("save_ability_choices", [])),
                damage_components=action.get("damage_components", []),
                target_scope=str(action.get("target_scope", "enemies")),
                damage=damage, damage_type=action.get("damage_type"),
                success_damage=str(action.get("success_damage", "none")),
                failure_sets_zero_hp=bool(action.get("failure_sets_zero_hp", False)),
                damage_only_on_success=bool(action.get("damage_only_on_success", False)),
                requires_target_hearing=bool(action.get("requires_target_hearing", False)),
                excluded_target_creature_types=list(action.get("excluded_target_creature_types", [])),
                prohibited_environment_context_id=action.get("prohibited_environment_context_id"),
                resource_id=action.get("resource_id"),
                resource_cost=int(action.get("resource_cost", 1) or 1),
                requires_no_active_grapple=bool(action.get("requires_no_active_grapple", False)),
                magical_effect=bool(action.get("magical_effect", False)),
                effect_tags=sorted(effect_tags),
                failed_save_timed_effect=rider,
                source_effect_immunity_on_success=bool(
                    action.get("source_effect_immunity_on_success", False)
                ),
                failed_save_push_ft=int(action.get("failure_push_ft", 0) or 0),
                animation=str(action.get("animation", "save-effect")),
            ))
        result.extend(source_proven_asymmetric_saves_2014(monster))
        result.extend(source_proven_visual_saves_2014(monster))
        result.extend(source_proven_conditioned_saves_2014(monster))
        result.extend(source_proven_opening_area_saves_2014(monster))
        result.extend(source_proven_audible_maintained_controls_2014(monster))
        return result
    except Exception:
        logger.exception("Failed to adapt 2014 save actions for %s.", monster.name)
        raise


def save_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    ids = {
        action.resource_id for action in save_capabilities_2014(monster)
        if action.resource_id is not None and action.resource_id in monster.action_recharges
    }
    resources = [
        ResourceDefinition(id=resource_id, name=resource_id.replace("-", " ").title(), max_uses=1)
        for resource_id in sorted(ids)
    ]
    for action in source_proven_asymmetric_saves_2014(monster):
        if action.resource_id and action.resource_id not in ids:
            resources.append(ResourceDefinition(
                id=action.resource_id, name=action.name, max_uses=1,
            ))
    return resources


def recharge_rules_2014(monster: SourceMonster2014) -> list[RechargeRule]:
    if not supports_recharge_rules_2014(monster):
        return []
    excluded_ids = arena_unavailable_recharge_ids_2014(monster)
    return [
        RechargeRule(resource_id=action_id, minimum_roll=minimum)
        for action_id, minimum in sorted(monster.action_recharges.items())
        if action_id not in excluded_ids
    ]
