from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.content.canonical_hero_policy import canonical_spell_package
from app.content.certified_heroes import build_all_certified_hero_entries
from app.content.class_spell_progression import CASTING_ABILITIES
from app.domain.models import CombatantTemplate, WeaponAttack

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-heroes.js"


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _control(effect: Any) -> dict[str, Any] | None:
    if effect is None:
        return None
    return {
        "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
        "grappleEscapeDc": effect.grapple_escape_dc,
        "restrainsWhileGrappled": effect.restrains_while_grappled,
        "conditionId": effect.condition_id,
        "expiresAtStartOfSourceTurn": effect.expires_at_start_of_source_turn,
        "expiryTiming": effect.expiry_timing,
        "repeatSaveAbility": effect.repeat_save_ability,
        "repeatSaveDc": effect.repeat_save_dc,
        "repeatSaveTiming": effect.repeat_save_timing,
        "allowedRemovalActionIds": list(effect.allowed_removal_action_ids),
    }


def _attack(attack: WeaponAttack) -> dict[str, Any]:
    if attack.conditional_damage:
        raise ValueError(f"Browser hero exporter has no certified conditional-damage mapping for {attack.id}.")
    weapon = attack.weapon
    row: dict[str, Any] = {
        "id": attack.id, "weaponId": weapon.id, "name": weapon.name, "kind": weapon.attack_kind.value,
        "bonus": attack.attack_bonus, "diceCount": weapon.dice_count, "diceSize": weapon.dice_size,
        "damageBonus": attack.damage_bonus, "damageType": weapon.damage_type.value,
        "reach": weapon.reach_ft, "animation": weapon.animation,
    }
    if attack.damage_source_qualifiers: row["damageSourceQualifiers"] = [_value(item) for item in attack.damage_source_qualifiers]
    if weapon.mastery_property is not None: row["masteryProperty"] = weapon.mastery_property
    if weapon.light: row["light"] = True
    if attack.damage_die_minimum is not None: row["damageDieMinimum"] = attack.damage_die_minimum
    if attack.attack_ability is not None: row["attackAbility"] = attack.attack_ability
    if attack.attack_ability_modifier is not None: row["attackAbilityModifier"] = attack.attack_ability_modifier
    if weapon.normal_range_ft is not None: row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
    if attack.fixed_damage is not None: row["fixedDamage"] = attack.fixed_damage
    if attack.rage_eligible: row["rageEligible"] = True
    if attack.sneak_attack_eligible: row["sneakAttackEligible"] = True
    if attack.knocks_prone_max_size is not None: row["proneMaxSize"] = attack.knocks_prone_max_size.value
    if attack.on_hit_damage:
        row["onHitDamage"] = [{"source": part.source, "diceCount": part.dice_count, "diceSize": part.dice_size,
                               "damageBonus": part.damage_bonus, "damageType": part.damage_type.value}
                              for part in attack.on_hit_damage]
    control = _control(attack.control_effect)
    if control: row["controlEffect"] = control
    return row


def _save(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost, "saveAbility": action.save_ability, "dc": action.dc,
        "range": action.range_ft, "targetMaxSize": _value(action.target_max_size) if action.target_max_size else None,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type,
        "successDamage": action.success_damage,
        "grappleEscapeDc": action.grapple_escape_dc, "restrainsWhileGrappled": action.restrains_while_grappled,
        "magicalEffect": action.magical_effect, "animation": action.animation,
    }
    if action.area is not None:
        row["area"] = action.area.model_dump(mode="json")
    if action.resource_id:
        row["resourceId"] = action.resource_id
        row["resourceCost"] = action.resource_cost
    if action.effect_tags:
        row["effectTags"] = list(action.effect_tags)
    if action.damage_components:
        row["damageComponents"] = [
            {"diceCount": item.dice_count, "diceSize": item.dice_size,
             "damageBonus": item.damage_bonus, "damageType": item.damage_type}
            for item in action.damage_components
        ]
    if action.failed_save_timed_effect is not None:
        row["failedSaveTimedEffect"] = {
            "effectId": action.failed_save_timed_effect.effect_id,
            "durationRounds": action.failed_save_timed_effect.duration_rounds,
            "expiryTiming": action.failed_save_timed_effect.expiry_timing,
            "repeatSaveAbility": action.failed_save_timed_effect.repeat_save_ability,
            "repeatSaveDc": action.failed_save_timed_effect.repeat_save_dc,
            "repeatSaveTiming": action.failed_save_timed_effect.repeat_save_timing,
            "nextAttackDisadvantage": action.failed_save_timed_effect.next_attack_disadvantage,
        }
    return row


def _spell(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
        "range": action.range_ft, "saveAbility": action.save_ability, "dc": action.dc,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type,
        "successDamage": action.success_damage, "upcastDicePerLevel": action.upcast_dice_per_level,
        "concentration": action.concentration, "animation": action.animation,
    }
    if action.effect_tags: row["effectTags"] = list(action.effect_tags)
    if action.failed_save_modifier_effects:
        row["failedSaveModifierEffects"] = [_modifier_effect(effect) for effect in action.failed_save_modifier_effects]
    if action.area is not None: row["area"] = action.area.model_dump(mode="json")
    if action.duration_minutes is not None: row["durationMinutes"] = action.duration_minutes
    if action.area_radius_ft is not None: row["areaRadius"] = action.area_radius_ft
    if action.damage_components:
        row["damageComponents"] = [
            {"diceCount": item.dice_count, "diceSize": item.dice_size,
             "damageBonus": item.damage_bonus, "damageType": item.damage_type}
            for item in action.damage_components
        ]
    return row


def _modifier_effect(effect: Any) -> dict[str, Any]:
    row = {"kind": effect.kind, "flatBonus": effect.flat_bonus, "diceCount": effect.dice_count,
           "diceSize": effect.dice_size, "damageType": effect.damage_type}
    if effect.minimum_value: row["minimumValue"] = effect.minimum_value
    if effect.condition_id: row["conditionId"] = effect.condition_id
    if effect.debuff_counter is not None: row["debuffCounter"] = effect.debuff_counter.model_dump(mode="json")
    if effect.replacement_hp: row["replacementHp"] = effect.replacement_hp
    if effect.prevents_instant_death: row["preventsInstantDeath"] = True
    if effect.source_creature_types: row["sourceCreatureTypes"] = list(effect.source_creature_types)
    if effect.save_ability: row["saveAbility"] = effect.save_ability
    if effect.save_dc is not None: row["saveDc"] = effect.save_dc
    if effect.consume_on_attack_against: row["consumeOnAttackAgainst"] = True
    if effect.ends_on_owner_attack: row["endsOnOwnerAttack"] = True
    if effect.expires_after_source_turns is not None: row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
    if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
    return row


def _spell_attack(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
           "attackKind": action.attack_kind, "range": action.range_ft, "attackBonus": action.attack_bonus,
           "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
           "damageBonus": action.damage_bonus, "damageType": action.damage_type,
           "attackCount": action.attack_count, "attacksPerSlotAbove": action.attacks_per_slot_above,
           "advantageIfTargetWearingMetalArmor": action.advantage_if_target_wearing_metal_armor,
           "onHitModifierEffects": [_modifier_effect(effect) for effect in action.on_hit_modifier_effects],
           "onHitTimedEffects": [
               {
                   "effectId": effect.effect_id,
                   "durationRounds": effect.duration_rounds,
                   "expiryTiming": effect.expiry_timing,
                   "suppressAction": effect.suppress_action,
                   "suppressBonusAction": effect.suppress_bonus_action,
                   "suppressReactions": effect.suppress_reactions,
                   "suppressMovement": effect.suppress_movement,
                   "nextAttackDisadvantage": effect.next_attack_disadvantage,
                   "sourceIsMagical": effect.source_is_magical,
               }
               for effect in action.on_hit_timed_effects
           ],
           "animation": action.animation}
    if action.source: row["source"] = action.source
    return row


def _auto_hit_spell(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "level": action.level,
        "actionCost": action.action_cost, "range": action.range_ft,
        "projectileCount": action.projectile_count,
        "projectilesPerSlotAbove": action.projectiles_per_slot_above,
        "damageDiceCount": action.damage_dice_count,
        "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type,
        "animation": action.animation,
    }
    if action.source: row["source"] = action.source
    return row


def _persistent_spell_attack(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id,
            "name": action.name,
            "attack": _spell_attack(action.attack),
            "durationRounds": action.duration_rounds,
            "moveFt": action.move_ft,
            "attackReachFt": action.attack_reach_ft,
            "upcastIntervalLevels": action.upcast_interval_levels,
        }
    except Exception:
        logger.exception("Failed to serialize persistent spell attack %s.", action.id)
        raise


def _persistent_hazard(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "castRangeFt": action.cast_range_ft,
            "durationRounds": action.duration_rounds, "footprintSize": _value(action.footprint_size),
            "triggerRadiusFt": action.trigger_radius_ft, "saveAbility": action.save_ability,
            "dc": action.dc, "failureDamage": action.failure_damage,
            "successDamage": action.success_damage, "damageType": action.damage_type,
            "maxTotalDamage": action.max_total_damage, "animation": action.animation,
            "source": action.source,
        }
    except Exception:
        logger.exception("Failed to serialize persistent hazard %s.", action.id)
        raise


def _defense(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
           "range": action.range_ft, "durationMinutes": action.duration_minutes,
           "targetPolicy": action.target_policy, "targetCount": action.target_count,
           "targetCountPerSlotAbove": action.target_count_per_slot_above,
           "temporaryHp": action.temporary_hp, "temporaryHpPerSlotAbove": action.temporary_hp_per_slot_above,
           "maxHpIncrease": action.max_hp_increase, "currentHpIncrease": action.current_hp_increase,
           "damageResistances": list(action.damage_resistances),
           "modifierEffects": [_modifier_effect(effect) for effect in action.modifier_effects],
           "concentration": action.concentration, "priority": action.priority, "animation": action.animation}
    if action.source: row["source"] = action.source
    return row


def _healing(action: Any) -> dict[str, Any]:
    try:
        return {"id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
                "targetMode": action.target_mode, "maxTargets": action.max_targets, "areaRadiusFt": action.area_radius_ft,
                "diceCount": action.dice_count, "diceSize": action.dice_size,
                "healingBonus": action.healing_bonus, "restoreToEffectiveMax": action.restore_to_effective_max,
                "percentileSuccessMax": action.percentile_success_max, "resourceId": action.resource_id,
                "resourceCost": action.resource_cost, "excludedCreatureTypes": list(action.excluded_creature_types),
                "removableConditions": list(action.removable_conditions),
                "proneReactionStand": action.prone_reaction_stand,
                "secondaryTargetWithinFt": action.secondary_target_within_ft,
                "animation": action.animation}
    except Exception:
        logger.exception("Failed to serialize healing action %s.", action.id)
        raise


def _targeted_concentration_damage(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "level": action.level,
        "actionCost": action.action_cost, "range": action.range_ft,
        "diceCount": action.dice_count, "diceSize": action.dice_size,
        "damageType": action.damage_type,
        "durationRoundsBySlot": dict(action.duration_rounds_by_slot),
        "retargetAfterTargetZero": action.retarget_after_target_zero,
        "priority": action.priority, "animation": action.animation, "source": action.source,
    }


def _d20_bonus_die_action(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "range": action.range_ft, "targetMode": action.target_mode,
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "diceCount": action.dice_count, "diceSize": action.dice_size,
            "testKinds": list(action.test_kinds), "durationRounds": action.duration_rounds,
            "priority": action.priority, "animation": action.animation,
            **({"exclusiveGroup": action.exclusive_group} if action.exclusive_group else {}),
        }
    except Exception:
        logger.exception("Failed to serialize d20 bonus-die action %s.", action.id)
        raise


def _reaction_roll_penalty(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "range": action.range_ft,
        "resourceId": action.resource_id, "resourceCost": action.resource_cost,
        "diceCount": action.dice_count, "diceSize": action.dice_size,
        "rollKinds": list(action.roll_kinds),
        "requiresSourceSight": action.requires_source_sight,
        "requiresTargetHearing": action.requires_target_hearing,
        "blockedTargetConditionImmunity": action.blocked_target_condition_immunity,
        "priority": action.priority, "animation": action.animation,
    }


def _save_advantage_grant(grant: Any) -> dict[str, Any]:
    row = grant.model_dump(mode="json")
    if not grant.required_effect_tags:
        row.pop("required_effect_tags", None)
    return row



def _passive_modifier_grant(grant: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source_id": grant.source_id,
        "source_name": grant.source_name,
        "kind": grant.kind,
        "condition_id": grant.condition_id,
        "source_creature_types": list(grant.source_creature_types),
    }
    if grant.required_active_effect_ids:
        row["required_active_effect_ids"] = list(grant.required_active_effect_ids)
    if grant.save_ability is not None:
        row["save_ability"] = grant.save_ability
    if grant.save_dc is not None:
        row["save_dc"] = grant.save_dc
    if grant.ends_on_owner_attack:
        row["ends_on_owner_attack"] = True
    if grant.success_immunity_hours is not None:
        row["success_immunity_hours"] = grant.success_immunity_hours
    return row

def _timed_self_buff(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost,
        "resourceId": action.resource_id, "resourceCost": action.resource_cost,
        "durationRounds": action.duration_rounds, "conditionIds": list(action.condition_ids),
        "damageResistances": [_value(item) for item in action.damage_resistances],
        "expiryTiming": action.expiry_timing, "priority": action.priority,
        "animation": action.animation,
    }
    if action.debuff_counters:
        row["debuffCounters"] = [item.model_dump(mode="json") for item in action.debuff_counters]
    if action.movement_mode_grants:
        row["movementModeGrants"] = [
            {
                "mode": item.mode,
                "fixedSpeedFt": item.fixed_speed_ft,
                "matchCurrentSpeed": item.match_current_speed,
            }
            for item in action.movement_mode_grants
        ]
    if action.saving_throw_advantage_grants:
        row["savingThrowAdvantageGrants"] = [
            _save_advantage_grant(item) for item in action.saving_throw_advantage_grants
        ]
    if action.ends_if_source_incapacitated:
        row["endsIfSourceIncapacitated"] = True
    if action.ends_if_source_dead:
        row["endsIfSourceDead"] = True
    if action.friendly_save_advantage_aura is not None:
        row["friendlySaveAdvantageAura"] = action.friendly_save_advantage_aura.model_dump(mode="json")
    if action.hostile_start_turn_condition_aura is not None:
        row["hostileStartTurnConditionAura"] = action.hostile_start_turn_condition_aura.model_dump(mode="json")
    if action.concentration:
        row["concentration"] = True
    if action.start_turn_emanation_damage is not None:
        row["startTurnEmanationDamage"] = action.start_turn_emanation_damage.model_dump(mode="json")
    return row


def _removal(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
           "targetMode": action.target_mode, "removableConditions": list(action.removable_conditions),
           "maxConditionsPerUse": action.max_conditions_per_use, "resourceCosts": dict(action.resource_costs),
           "resourceCostsPerCondition": dict(action.resource_costs_per_condition),
           "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation}
    if action.reaction_trigger: row["reactionTrigger"] = action.reaction_trigger
    return row


def _spell_choice(choice: Any) -> dict[str, Any]:
    return {"id": choice.id, "name": choice.name, "level": choice.spell_level,
            "role": choice.role, "requiredCapabilities": list(choice.required_capabilities)}


def _effect_removal(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "level": action.level,
        "actionCost": action.action_cost, "range": action.range_ft,
        "castingAbility": action.casting_ability, "targetMode": action.target_mode,
        "autoRemoveMaxLevel": action.auto_remove_max_level,
        "resourceId": action.resource_id, "resourceCost": action.resource_cost,
        "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
    }


def _resource_conversion(action: Any) -> dict[str, Any]:
    return {
        "id": action.id,
        "name": action.name,
        "actionCost": action.action_cost,
        "sourceResourceId": action.source_resource_id,
        "sourceCost": action.source_cost,
        "targetResourceId": action.target_resource_id,
        "targetGain": action.target_gain,
        "targetAllowsOverflow": action.target_allows_overflow,
        "automation": action.automation,
        "priority": action.priority,
        "source": action.source,
    }


def _spell_package(class_id: str, level: int, template: CombatantTemplate):
    if not (
        template.spell_save_actions or template.spell_attack_actions or template.auto_hit_spell_actions
        or template.persistent_spell_attack_actions
        or template.persistent_hazard_actions or template.defensive_spell_actions or template.healing_actions
    ):
        return None
    casting_modifier = None
    casting_ability = CASTING_ABILITIES.get(class_id)
    if casting_ability is not None and template.ability_scores is not None:
        casting_modifier = template.ability_scores.modifier(casting_ability)
    return canonical_spell_package(class_id, level, template.ruleset, casting_modifier)


def _template(key: tuple[str, int, str], template: CombatantTemplate) -> dict[str, Any]:
    class_id, level, build_id = key; attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    progression = template.progression_features
    row: dict[str, Any] = {
        "id": template.id, "class_id": class_id, "build_id": build_id, "name": template.name,
        "archetype": template.archetype, "level": template.level, "kind": template.kind,
        "ruleset": template.ruleset, "size": template.size.value,
        "ability_scores": template.ability_scores.model_dump() if template.ability_scores else None,
        "armor_class": template.armor_class, "max_hp": template.max_hp, "speed_ft": template.speed_ft,
        "initiative_bonus": template.initiative_bonus, "saving_throw_bonuses": template.saving_throw_bonuses,
        "skill_bonuses": template.skill_bonuses, "attacks": [_attack(item) for item in attacks],
        "primary_attack_id": template.weapon_attack.id, "saving_throw_actions": [_save(item) for item in template.saving_throw_actions],
        "hp_threshold_condition_actions": [
            {
                "id": item.id, "name": item.name, "actionCost": item.action_cost,
                "range": item.range_ft, "maxCurrentHp": item.max_current_hp,
                "conditionId": item.condition_id, "repeatSaveAbility": item.repeat_save_ability,
                "repeatSaveDc": item.repeat_save_dc, "repeatSaveTiming": item.repeat_save_timing,
                "resourceId": item.resource_id, "resourceCost": item.resource_cost,
                "magicalEffect": item.magical_effect, "animation": item.animation,
            }
            for item in template.hp_threshold_condition_actions
        ],
        "hp_threshold_instant_death_actions": [
            {
                "id": item.id, "name": item.name, "actionCost": item.action_cost,
                "range": item.range_ft, "maxCurrentHp": item.max_current_hp,
                "fallbackDamageDiceCount": item.fallback_damage_dice_count,
                "fallbackDamageDiceSize": item.fallback_damage_dice_size,
                "fallbackDamageBonus": item.fallback_damage_bonus,
                "fallbackDamageType": item.fallback_damage_type,
                "resourceId": item.resource_id, "resourceCost": item.resource_cost,
                "magicalEffect": item.magical_effect, "maxTargets": item.max_targets,
                "secondaryTargetWithinFt": item.secondary_target_within_ft,
                "animation": item.animation,
            }
            for item in template.hp_threshold_instant_death_actions
        ],
        "healingActions": [_healing(item) for item in template.healing_actions],
        "persistent_hazard_actions": [_persistent_hazard(item) for item in template.persistent_hazard_actions],
        "damage_resistances": [item.value for item in template.damage_resistances],
        "damage_vulnerabilities": [item.value for item in template.damage_vulnerabilities],
        "damage_immunities": [item.value for item in template.damage_immunities],
        "condition_immunities": list(template.condition_immunities),
            "wearing_metal_armor": template.wearing_metal_armor,
        "passive_modifier_grants": [_passive_modifier_grant(item) for item in template.passive_modifier_grants],
        "timed_self_buff_actions": [_timed_self_buff(item) for item in template.timed_self_buff_actions],
        "traits": [item.value for item in template.combat_traits], "resources": {item.id: item.max_uses for item in template.resources},
        "rage_damage_bonus": template.rage_damage_bonus, "wearing_heavy_armor": template.wearing_heavy_armor,
        "wearing_metal_armor": template.wearing_metal_armor,
        "fighting_style": template.fighting_style, "fighting_styles": list(template.fighting_styles),
        "weapon_masteries": list(template.weapon_masteries), "critical_hit_minimum": progression.critical_hit_minimum,
        "initiative_advantage": progression.initiative_advantage, "athletics_advantage": progression.athletics_advantage,
        "first_round_extra_turn_initiative_offset": progression.first_round_extra_turn_initiative_offset,
        "suppress_attack_advantage_while_not_incapacitated": progression.suppress_attack_advantage_while_not_incapacitated,
        "ignore_unseen_target_attack_disadvantage": progression.ignore_unseen_target_attack_disadvantage,
        "miss_to_hit_override_resource_id": progression.miss_to_hit_override_resource_id,
        "miss_to_hit_override_source_name": progression.miss_to_hit_override_source_name,
        "start_turn_resource_refill_ids": list(progression.start_turn_resource_refill_ids),
        "failed_save_reroll_grants": [
            item.model_dump(exclude_unset=True, exclude_none=True)
            for item in progression.failed_save_reroll_grants
        ],
        "failed_d20_test_override_grants": [item.model_dump() for item in progression.failed_d20_test_override_grants],
        "deferred_save_effect": progression.deferred_save_effect.model_dump() if progression.deferred_save_effect else None,
        "area_spell_ally_protection": (
            progression.area_spell_ally_protection.model_dump()
            if progression.area_spell_ally_protection else None
        ),
        "alternate_spell_cast_grants": [
            item.model_dump() for item in progression.alternate_spell_cast_grants
        ],
        "spell_damage_maximizer": (
            progression.spell_damage_maximizer.model_dump()
            if progression.spell_damage_maximizer else None
        ),
        "opening_targeting_ward": progression.opening_targeting_ward.model_dump() if progression.opening_targeting_ward else None,
        "danger_sense": progression.danger_sense, "reckless_attack": progression.reckless_attack,
        "frenzy": progression.frenzy, "frenzy_bonus_attack_2014": progression.frenzy_bonus_attack_2014,
        "persistent_rage_2014": progression.persistent_rage_2014,
        "rage_persists_without_maintenance": progression.rage_persists_without_maintenance,
        "intimidating_presence_2014_dc": progression.intimidating_presence_2014_dc,
        "brutal_critical_dice": progression.brutal_critical_dice,
        "brutal_strike_damage_dice": progression.brutal_strike_damage_dice,
        "brutal_strike_effect_ids": list(progression.brutal_strike_effect_ids),
        "brutal_strike_max_effects": progression.brutal_strike_max_effects,
        "fast_movement_bonus_ft": progression.fast_movement_bonus_ft,
        "mindless_rage": progression.mindless_rage, "instinctive_pounce_fraction": progression.instinctive_pounce_fraction,
        "great_weapon_fighting": progression.great_weapon_fighting, "sneak_attack_d6": progression.sneak_attack_d6,
        "cunning_action": progression.cunning_action,
        "stationary_bonus_action_next_attack_advantage": progression.stationary_bonus_action_next_attack_advantage,
        "cunning_strike_trip_die_cost": progression.cunning_strike_trip_die_cost,
        "cunning_strike_obscure_die_cost": progression.cunning_strike_obscure_die_cost,
        "cunning_strike_max_effects": progression.cunning_strike_max_effects,
        "saving_throw_proficiency_grants": [
            item.model_dump() for item in progression.saving_throw_proficiency_grants
        ],
        "saving_throw_advantage_grants": [
            _save_advantage_grant(item) for item in progression.saving_throw_advantage_grants
        ],
        "passive_debuff_counter_grants": [
            item.model_dump(mode="json") for item in progression.passive_debuff_counter_grants
        ],
        "first_round_extra_turn_grants": [
            item.model_dump() for item in progression.first_round_extra_turn_grants
        ],
        "uncanny_dodge": progression.uncanny_dodge, "evasion": progression.evasion, "martial_arts_bonus_attack": progression.martial_arts_bonus_attack,
        "martial_arts_die_size": progression.martial_arts_die_size, "flurry_of_blows": progression.flurry_of_blows,
        "deflect_missiles": progression.deflect_missiles, "open_hand_technique": progression.open_hand_technique,
        "stunning_strike": progression.stunning_strike,
        "divine_smite_2014": progression.divine_smite_2014, "turn_unholy_2014": progression.turn_unholy_2014,
        "sacred_weapon_2014_bonus": progression.sacred_weapon_2014_bonus,
        "aura_of_protection_2014_bonus": progression.aura_of_protection_2014_bonus,
        "aura_radius_2014_ft": progression.aura_radius_2014_ft,
        "aura_of_devotion_2014": progression.aura_of_devotion_2014,
        "aura_of_courage_2014": progression.aura_of_courage_2014,
        "survivor_heal_amount": progression.survivor_heal_amount,
        "bloodied_start_turn_heal_amount": progression.bloodied_start_turn_heal_amount,
        "death_save_advantage": progression.death_save_advantage,
        "death_save_recovery_minimum": progression.death_save_recovery_minimum,
        "critical_move_fraction": progression.critical_move_fraction, "tactical_shift_fraction": progression.tactical_shift_fraction,
        "visual": {"armor": template.visual.armor, "main_hand": template.visual.main_hand,
                   "off_hand": template.visual.off_hand, "body_style": template.visual.body_style,
                   "figure_form": template.visual.body_style, "role": template.archetype.lower()},
        "selectable_damage_resistance": (
            template.progression_features.selectable_damage_resistance.model_dump(mode="json")
            if template.progression_features.selectable_damage_resistance else None
        ),
        "resource_backed_on_hit_exile": (
            template.progression_features.resource_backed_on_hit_exile.model_dump(mode="json")
            if template.progression_features.resource_backed_on_hit_exile else None
        ),
        "conditional_damage_defenses": [
            {
                "id": item.id, "kind": _value(item.kind),
                "damageTypes": [_value(kind) for kind in item.damage_types],
                "requiredSourceQualifiers": [_value(kind) for kind in item.required_source_qualifiers],
                "forbiddenSourceQualifiers": [_value(kind) for kind in item.forbidden_source_qualifiers],
            }
            for item in template.conditional_damage_defenses
        ],
        "source": template.source,
    }
    if progression.source_reduces_hostile_to_zero_hp_temporary_hp is not None:
        row["source_reduces_hostile_to_zero_hp_temporary_hp"] = (
            progression.source_reduces_hostile_to_zero_hp_temporary_hp.model_dump(mode="json")
        )
    if progression.source_damage_temporary_hp is not None:
        row["source_damage_temporary_hp"] = progression.source_damage_temporary_hp.model_dump(mode="json")
    if progression.delayed_resource_refill is not None:
        row["delayed_resource_refill"] = progression.delayed_resource_refill.model_dump(mode="json")
    if template.unlimited_resource_ids:
        row["unlimited_resources"] = list(template.unlimited_resource_ids)
    if template.initiative_resource_refill_grants:
        row["initiative_resource_refill_grants"] = [
            {key: value for key, value in item.model_dump().items() if key != "restore_to_minimum" or value is not None} for item in template.initiative_resource_refill_grants
        ]
    if template.resource_conversion_actions:
        row["resource_conversion_actions"] = [
            _resource_conversion(item) for item in template.resource_conversion_actions
        ]
    if template.spell_save_disadvantage_options:
        row["spellSaveDisadvantageOptions"] = [
            {
                "id": item.id, "name": item.name, "resourceId": item.resource_id,
                "resourceCost": item.resource_cost, "targetPolicy": item.target_policy,
                "priority": item.priority, "source": item.source,
            }
            for item in template.spell_save_disadvantage_options
        ]
    if template.spell_range_modifiers:
        row["spellRangeModifiers"] = [
            {
                "id": item.id, "name": item.name, "resourceId": item.resource_id,
                "resourceCost": item.resource_cost, "rangeMultiplier": item.range_multiplier,
                "minimumBaseRangeFt": item.minimum_base_range_ft,
                "priority": item.priority, "source": item.source,
            }
            for item in template.spell_range_modifiers
        ]
    if template.spell_duration_modifiers:
        row["spellDurationModifiers"] = [
            {
                "id": item.id, "name": item.name, "resourceId": item.resource_id,
                "resourceCost": item.resource_cost, "durationMultiplier": item.duration_multiplier,
                "maximumDurationMinutes": item.maximum_duration_minutes,
                "minimumBaseDurationMinutes": item.minimum_base_duration_minutes,
                "priority": item.priority, "source": item.source,
            }
            for item in template.spell_duration_modifiers
        ]
    if progression.effect_bound_survival_save:
        row["effect_bound_survival_save"] = progression.effect_bound_survival_save.model_dump()
    if progression.turning_failure_damage:
        row["turning_failure_damage"] = progression.turning_failure_damage.model_dump()
    if progression.turning_failure_destroy_max_cr:
        row["turning_failure_destroy_max_cr"] = progression.turning_failure_destroy_max_cr
    if progression.slot_healing_other_self_rider:
        row["slot_healing_other_self_rider"] = progression.slot_healing_other_self_rider.model_dump()
    if template.d20_bonus_die_actions:
        row["d20BonusDieActions"] = [_d20_bonus_die_action(item) for item in template.d20_bonus_die_actions]
    if template.reaction_roll_penalty_actions:
        row["reactionRollPenaltyActions"] = [_reaction_roll_penalty(item) for item in template.reaction_roll_penalty_actions]
    if progression.outgoing_healing_dice_maximizer:
        row["outgoing_healing_dice_maximizer"] = progression.outgoing_healing_dice_maximizer.model_dump()
    if progression.once_per_turn_weapon_hit_damage_rider:
        row["once_per_turn_weapon_hit_damage_rider"] = progression.once_per_turn_weapon_hit_damage_rider.model_dump()
    if progression.once_per_turn_weapon_hit_damage_riders:
        row["once_per_turn_weapon_hit_damage_riders"] = [
            item.model_dump() for item in progression.once_per_turn_weapon_hit_damage_riders
        ]
    if progression.ability_check_minimums:
        row["ability_check_minimums"] = [item.model_dump() for item in progression.ability_check_minimums]
    if progression.damage_resistance_bypass_grants:
        row["damage_resistance_bypass_grants"] = [
            item.model_dump(mode="json") for item in progression.damage_resistance_bypass_grants
        ]
    if progression.natural_twenty_attack_damage_grants:
        row["natural_twenty_attack_damage_grants"] = [
            item.model_dump(mode="json") for item in progression.natural_twenty_attack_damage_grants
        ]
    if progression.saving_throw_minimums:
        row["saving_throw_minimums"] = [item.model_dump() for item in progression.saving_throw_minimums]
    if progression.resource_backed_d20_bonus_dice:
        row["resource_backed_d20_bonus_dice"] = [
            item.model_dump() for item in progression.resource_backed_d20_bonus_dice
        ]
    if progression.resource_backed_d20_outcome_adjustments:
        row["resource_backed_d20_outcome_adjustments"] = [
            item.model_dump(mode="json") for item in progression.resource_backed_d20_outcome_adjustments
        ]
    if progression.indomitable_reroll: row["indomitable_reroll"] = True
    if progression.indomitable_bonus: row["indomitable_bonus"] = progression.indomitable_bonus
    if progression.tactical_master_sap_weapon_ids: row["tactical_master_sap_weapon_ids"] = list(progression.tactical_master_sap_weapon_ids)
    if progression.heroic_warrior: row["heroic_warrior"] = True
    if progression.studied_attacks: row["studied_attacks"] = True
    package = _spell_package(class_id, level, template)
    if package is not None:
        row["canonical_cantrips"] = [_spell_choice(item) for item in package.cantrips]
        row["canonical_prepared_spells"] = [_spell_choice(item) for item in package.spells]
        row["canonical_always_prepared_spells"] = [_spell_choice(item) for item in package.always_prepared_spells]
    if template.spell_save_actions: row["spell_save_actions"] = [_spell(item) for item in template.spell_save_actions]
    if template.spell_attack_actions: row["spell_attack_actions"] = [_spell_attack(item) for item in template.spell_attack_actions]
    if template.targeted_concentration_damage_actions:
        row["targeted_concentration_damage_actions"] = [
            _targeted_concentration_damage(item) for item in template.targeted_concentration_damage_actions
        ]
    if template.auto_hit_spell_actions: row["auto_hit_spell_actions"] = [_auto_hit_spell(item) for item in template.auto_hit_spell_actions]
    if template.persistent_spell_attack_actions:
        row["persistent_spell_attack_actions"] = [_persistent_spell_attack(item) for item in template.persistent_spell_attack_actions]
    if template.defensive_spell_actions: row["defensive_spell_actions"] = [_defense(item) for item in template.defensive_spell_actions]
    if template.condition_removal_actions: row["condition_removal_actions"] = [_removal(item) for item in template.condition_removal_actions]
    if template.effect_removal_actions: row["effect_removal_actions"] = [_effect_removal(item) for item in template.effect_removal_actions]
    if template.replacement_form_actions:
        row["replacement_form_actions"] = [
            {
                "id": item.id,
                "name": item.name,
                "actionCost": item.action_cost,
                "formTemplateId": item.form_template_id,
                "resourceId": item.resource_id,
                "resourceCost": item.resource_cost,
                "voluntaryRevertAction": item.voluntary_revert_action,
                "hpMode": item.hp_mode,
                "temporaryHpOnEnter": item.temporary_hp_on_enter,
                "retainCreatureType": item.retain_creature_type,
                "retainSpellcasting": item.retain_spellcasting,
                **({"retainedSpellActionIds": list(item.retained_spell_action_ids)} if item.retained_spell_action_ids else {}),
                "setupSpellId": item.setup_spell_id,
                "source": item.source,
            }
            for item in template.replacement_form_actions
        ]
    if template.area_weapon_attack_actions:
        row["area_weapon_attack_actions"] = [
            {
                "id": item.id, "name": item.name, "attackId": item.attack_id,
                "range": item.range_ft, "area": item.area.model_dump(mode="json"),
                "actionCost": item.action_cost, "source": item.source,
            }
            for item in template.area_weapon_attack_actions
        ]
    if template.attack_action:
        row["attack_action"] = {"id": template.attack_action.id, "name": template.attack_action.name,
                                "isAttackAction": template.attack_action.is_attack_action,
                                "slots": [{"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
                                          for slot in template.attack_action.slots]}
    return row


def render() -> str:
    rows = [_template(key, template) for key, template in build_all_certified_hero_entries()]
    payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    return "/* GENERATED from audited Python RAW-ready hero templates. Do not hand-edit. */\n(() => {\n  \"use strict\";\n  const heroes = " + payload + ";\n  window.IRON_PIT_BROWSER_HEROES = Object.fromEntries(heroes.map((item) => [item.id, item]));\n})();\n"


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified browser heroes to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser hero export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
