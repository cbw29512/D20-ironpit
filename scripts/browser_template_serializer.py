from __future__ import annotations

import logging
from typing import Any

from app.combat.charge_profiles import charge_profile_for_attack
from app.domain.models import CombatantTemplate, WeaponAttack
from app.domain.traits import CombatTrait

try:
    from scripts.browser_recharge_serializer import recharge_rows
except ModuleNotFoundError:
    from browser_recharge_serializer import recharge_rows

logger = logging.getLogger(__name__)


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _control(effect: Any) -> dict[str, Any] | None:
    if effect is None:
        return None
    row: dict[str, Any] = {}
    if effect.max_target_size:
        row["maxTargetSize"] = _value(effect.max_target_size)
    if effect.grapple_escape_dc is not None:
        row["grappleEscapeDc"] = effect.grapple_escape_dc
    if effect.restrains_while_grappled:
        row["restrainsWhileGrappled"] = True
    if effect.condition_id:
        row["conditionId"] = effect.condition_id
        if effect.expires_at_start_of_source_turn:
            row["expiresAtStartOfSourceTurn"] = True
        if effect.expiry_timing:
            row["expiryTiming"] = effect.expiry_timing
        if effect.repeat_save_ability:
            row["repeatSaveAbility"] = effect.repeat_save_ability
            row["repeatSaveDc"] = effect.repeat_save_dc
            row["repeatSaveTiming"] = effect.repeat_save_timing
        if effect.allowed_removal_action_ids:
            row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
    return row or None


def _hit_modifier(effect: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"kind": effect.kind}
    if effect.flat_bonus:
        row["flatBonus"] = effect.flat_bonus
    if effect.consume_on_attack_against:
        row["consumeOnAttackAgainst"] = True
    if effect.expires_at_start_of_source_turn:
        row["expiresAtStartOfSourceTurn"] = True
    if effect.expires_at_end_of_target_turn:
        row["expiresAtEndOfTargetTurn"] = True
    return row


def attack_row(attack: WeaponAttack, traits: set[str]) -> dict[str, Any]:
    try:
        weapon = attack.weapon
        row: dict[str, Any] = {
            "id": attack.id, "name": weapon.name, "kind": weapon.attack_kind.value,
            "bonus": attack.attack_bonus, "diceCount": weapon.dice_count, "diceSize": weapon.dice_size,
            "damageBonus": attack.damage_bonus, "damageType": weapon.damage_type.value,
            "reach": weapon.reach_ft, "animation": weapon.animation,
        }
        if weapon.damage_type_choices:
            row["damageTypeChoices"] = [item.value for item in weapon.damage_type_choices]
        if attack.damage_source_qualifiers:
            row["damageSourceQualifiers"] = [_value(item) for item in attack.damage_source_qualifiers]
        if attack.attack_ability is not None:
            row["attackAbility"] = attack.attack_ability
        if weapon.normal_range_ft is not None:
            row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
        if attack.unavailable_reason is not None:
            row["unavailableReason"] = attack.unavailable_reason
        if attack.fixed_damage is not None:
            row["fixedDamage"] = attack.fixed_damage
        if attack.rage_eligible:
            row["rageEligible"] = True
        if attack.sneak_attack_eligible:
            row["sneakAttackEligible"] = True
        if attack.knocks_prone_max_size is not None:
            row["proneMaxSize"] = attack.knocks_prone_max_size.value
        if attack.forbid_target_grappled_by_self:
            row["forbidSelfGrappledTarget"] = True
        if attack.grapple_target_policy != "normal":
            row["grappleTargetPolicy"] = attack.grapple_target_policy
        if attack.conditional_attack_advantage:
            row["conditionalAttackAdvantage"] = [
                {"trigger": spec.trigger} for spec in attack.conditional_attack_advantage
            ]
        if attack.on_hit_damage:
            row["onHitDamage"] = [
                {"source": part.source, "diceCount": part.dice_count, "diceSize": part.dice_size,
                 "damageBonus": part.damage_bonus, "damageType": part.damage_type.value}
                for part in attack.on_hit_damage
            ]
        if attack.on_hit_save_damage:
            effect = attack.on_hit_save_damage
            save_damage = {
                "source": effect.source, "saveAbility": _value(effect.save_ability), "dc": effect.dc,
                "diceCount": effect.dice_count, "diceSize": effect.dice_size,
                "damageBonus": effect.damage_bonus, "damageType": effect.damage_type.value,
                "successDamage": effect.success_damage,
            }
            if effect.zero_hp_rider:
                rider = effect.zero_hp_rider
                save_damage["zeroHpRider"] = {
                    "stable": rider.stable,
                    "conditionIds": [_value(item) for item in rider.condition_ids],
                    "durationRounds": rider.duration_rounds,
                }
            row["onHitSaveDamage"] = save_damage
        if attack.on_hit_contested_movement:
            effect = attack.on_hit_contested_movement
            row["onHitContestedMovement"] = {
                "sourceAbility": _value(effect.source_ability),
                "targetAbility": _value(effect.target_ability),
                "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
                "distanceFt": effect.distance_ft,
                "direction": effect.direction,
            }
        if attack.on_hit_maximum_hp_save:
            effect = attack.on_hit_maximum_hp_save
            row["onHitMaximumHpSave"] = {
                "saveAbility": _value(effect.save_ability),
                "dc": effect.dc,
                "reduction": effect.reduction,
                "zeroMaxHpKills": effect.zero_max_hp_kills,
            }
        if attack.on_hit_condition_save:
            effect = attack.on_hit_condition_save
            save_row = {
                "saveAbility": _value(effect.save_ability), "dc": effect.dc,
                "conditionId": effect.condition_id,
                "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
            }
            if effect.duration_rounds is not None:
                save_row["durationRounds"] = effect.duration_rounds
            if effect.repeat_save_timing is not None:
                save_row["repeatSaveTiming"] = _value(effect.repeat_save_timing)
            if effect.repeat_save_failure_condition_id:
                save_row["repeatSaveFailureConditionId"] = effect.repeat_save_failure_condition_id
            if effect.failure_push_ft:
                save_row["failurePushFt"] = effect.failure_push_ft
            if effect.excluded_creature_types:
                save_row["excludedCreatureTypes"] = list(effect.excluded_creature_types)
            if effect.excluded_creature_subtypes:
                save_row["excludedCreatureSubtypes"] = list(effect.excluded_creature_subtypes)
            row["onHitConditionSave"] = save_row
        if attack.on_hit_modifier_effects:
            row["onHitModifiers"] = [_hit_modifier(effect) for effect in attack.on_hit_modifier_effects]
        if attack.conditional_damage:
            if len(attack.conditional_damage) != 1:
                raise ValueError(f"Browser supports one conditional damage rider on {attack.id}.")
            conditional = attack.conditional_damage[0]
            legacy = (
                conditional.trigger == "attack_advantage" and conditional.mode == "add"
                and conditional.damage_bonus == 0 and conditional.damage_type == weapon.damage_type
            )
            if legacy:
                row["conditionalAdvantage"] = [conditional.dice_count, conditional.dice_size]
            else:
                row["conditionalDamage"] = {
                    "trigger": conditional.trigger, "mode": conditional.mode,
                    "diceCount": conditional.dice_count, "diceSize": conditional.dice_size,
                    "damageBonus": conditional.damage_bonus, "damageType": conditional.damage_type.value,
                }
        control = _control(attack.control_effect)
        if control:
            row["controlEffect"] = control
        if CombatTrait.CHARGE.value in traits:
            profile = charge_profile_for_attack(attack)
            if profile:
                charge: dict[str, Any] = {"minimumMove": profile.minimum_move_ft}
                if profile.prone_max_target_size is not None:
                    charge["proneMaxSize"] = profile.prone_max_target_size.value
                if profile.prone_save_ability is not None:
                    charge["proneSaveAbility"] = _value(profile.prone_save_ability)
                    charge["proneSaveDc"] = profile.prone_save_dc
                if profile.max_target_size is not None and profile.max_target_size != profile.prone_max_target_size:
                    charge["targetMaxSize"] = profile.max_target_size.value
                if profile.bonus_damage is not None:
                    charge.update(
                        diceCount=profile.bonus_damage.dice_count,
                        diceSize=profile.bonus_damage.dice_size,
                        damageType=profile.bonus_damage.damage_type.value,
                    )
                    if profile.bonus_damage.damage_bonus:
                        charge["damageBonus"] = profile.bonus_damage.damage_bonus
                if profile.replacement_damage is not None:
                    replacement = profile.replacement_damage
                    charge["replacementDamage"] = {
                        "diceCount": replacement.dice_count, "diceSize": replacement.dice_size,
                        "damageBonus": replacement.damage_bonus, "damageType": replacement.damage_type.value,
                    }
                if profile.follow_up_attack_id:
                    charge["followUpAttackId"] = profile.follow_up_attack_id
                row["charge"] = charge
        return row
    except Exception:
        logger.exception("Failed to serialize attack %s for browser runtime.", attack.id)
        raise


def _save(action: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost, "saveAbility": action.save_ability, "dc": action.dc,
        "range": action.range_ft, "damageDiceCount": action.damage_dice_count,
        "damageDiceSize": action.damage_dice_size, "damageBonus": action.damage_bonus,
        "damageType": action.damage_type, "successDamage": action.success_damage, "animation": action.animation,
    }
    if action.damage_components:
        row["damageComponents"] = [
            {"diceCount": item.dice_count, "diceSize": item.dice_size,
             "damageBonus": item.damage_bonus, "damageType": item.damage_type}
            for item in action.damage_components
        ]
    if action.target_max_size:
        row["targetMaxSize"] = _value(action.target_max_size)
    if action.area:
        row["area"] = action.area.model_dump(mode="json")
    if action.resource_id:
        row["resourceId"] = action.resource_id
        row["resourceCost"] = action.resource_cost
    if action.requires_no_active_grapple:
        row["requiresNoActiveGrapple"] = True
    if action.magical_effect:
        row["magicalEffect"] = True
    if action.effect_tags:
        row["effectTags"] = list(action.effect_tags)
    if action.automatic_failure_creature_types:
        row["automaticFailureCreatureTypes"] = list(action.automatic_failure_creature_types)
    if action.requires_target_hearing:
        row["requiresTargetHearing"] = True
    if action.requires_target_sight:
        row["requiresTargetSight"] = True
    if action.area_healing_rider is not None:
        row["areaHealingRider"] = {
            "diceCount": action.area_healing_rider.dice_count,
            "diceSize": action.area_healing_rider.dice_size,
            "healingBonus": action.area_healing_rider.healing_bonus,
        }
    if action.failed_save_timed_effect is not None:
        row["failedSaveTimedEffect"] = _failed_save_timed_effect(action.failed_save_timed_effect)
    if action.source_effect_immunity_on_success:
        row["sourceEffectImmunityOnSuccess"] = True
    if action.grapple_escape_dc is not None:
        row["grappleEscapeDc"] = action.grapple_escape_dc
    if action.restrains_while_grappled:
        row["restrainsWhileGrappled"] = True
    return row


def _spell(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
        "range": action.range_ft, "saveAbility": action.save_ability, "dc": action.dc,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type,
        "successDamage": action.success_damage, "upcastDicePerLevel": action.upcast_dice_per_level,
        "concentration": action.concentration, "allowsHigherSlots": action.allows_higher_slots,
        "targetCount": action.target_count,
        "targetCountPerSlotAbove": action.target_count_per_slot_above,
        "saveAdvantageIfFighting": action.save_advantage_if_fighting,
        "castRounds": action.cast_rounds,
        "animation": action.animation,
    }
    if action.effect_tags:
        row["effectTags"] = list(action.effect_tags)
    if action.automatic_failure_creature_types:
        row["automaticFailureCreatureTypes"] = list(action.automatic_failure_creature_types)
    if action.requires_target_hearing:
        row["requiresTargetHearing"] = True
    if action.requires_target_sight:
        row["requiresTargetSight"] = True
    if action.failed_save_timed_effect is not None:
        row["failedSaveTimedEffect"] = _failed_save_timed_effect(action.failed_save_timed_effect)
    if action.required_target_creature_types:
        row["requiredTargetCreatureTypes"] = list(action.required_target_creature_types)
    if action.excluded_target_creature_types:
        row["excludedTargetCreatureTypes"] = list(action.excluded_target_creature_types)
    if action.minimum_remaining_hp:
        row["minimumRemainingHp"] = action.minimum_remaining_hp
    if action.reduce_hit_point_maximum_on_failed_save:
        row["reduceHitPointMaximumOnFailedSave"] = True
    if not action.verbal_component:
        row["verbalComponent"] = False
    if action.failed_save_push_ft:
        row["failedSavePushFt"] = action.failed_save_push_ft
    if action.failed_save_modifier_effects:
        row["failedSaveModifierEffects"] = [
            _modifier_effect(effect) for effect in action.failed_save_modifier_effects
        ]
    if action.area is not None:
        row["area"] = action.area.model_dump(mode="json")
    if action.creates_difficult_terrain:
        row["createsDifficultTerrain"] = True
        row["difficultTerrainDurationRounds"] = action.difficult_terrain_duration_rounds
    if action.duration_minutes is not None:
        row["durationMinutes"] = action.duration_minutes
    if action.area_radius_ft is not None:
        row["areaRadius"] = action.area_radius_ft
    if action.damage_components:
        row["damageComponents"] = [
            {"diceCount": item.dice_count, "diceSize": item.dice_size,
             "damageBonus": item.damage_bonus, "damageType": item.damage_type}
            for item in action.damage_components
        ]
    return row


def _failed_save_timed_effect(rider: Any) -> dict[str, Any]:
    row = {
        "effectId": rider.effect_id,
        "durationRounds": rider.duration_rounds,
        "expiryTiming": rider.expiry_timing,
        "repeatSaveAbility": rider.repeat_save_ability,
        "repeatSaveDc": rider.repeat_save_dc,
        "repeatSaveTiming": rider.repeat_save_timing,
        "turnBehavior": rider.turn_behavior,
        "endsOnDamage": rider.ends_on_damage,
        "endsIfSourceIncapacitated": rider.ends_if_source_incapacitated,
        "endsIfSourceDead": rider.ends_if_source_dead,
        "nextAttackDisadvantage": rider.next_attack_disadvantage,
        "repeatSaveFailuresToLock": rider.repeat_save_failures_to_lock,
    }
    if rider.escape_check_ability:
        row["escapeCheckAbility"] = rider.escape_check_ability
        row["escapeCheckDc"] = rider.escape_check_dc
    if rider.source_effect_immunity_on_end:
        row["sourceEffectImmunityOnEnd"] = True
    return row


def _modifier_effect(effect: Any) -> dict[str, Any]:
    row = {
        "kind": effect.kind, "flatBonus": effect.flat_bonus, "diceCount": effect.dice_count,
        "diceSize": effect.dice_size, "damageType": effect.damage_type,
    }
    if effect.condition_id:
        row["conditionId"] = effect.condition_id
    if effect.minimum_value:
        row["minimumValue"] = effect.minimum_value
    if effect.debuff_counter is not None:
        row["debuffCounter"] = effect.debuff_counter.model_dump(mode="json")
    if effect.replacement_hp:
        row["replacementHp"] = effect.replacement_hp
    if effect.prevents_instant_death:
        row["preventsInstantDeath"] = True
    if effect.source_creature_types:
        row["sourceCreatureTypes"] = list(effect.source_creature_types)
    if effect.required_effect_tags:
        row["requiredEffectTags"] = list(effect.required_effect_tags)
    if effect.save_ability is not None:
        row["saveAbility"] = effect.save_ability
    if effect.save_dc is not None:
        row["saveDc"] = effect.save_dc
    if effect.bypass_attacker_senses:
        row["bypassAttackerSenses"] = list(effect.bypass_attacker_senses)
    if effect.consume_on_attack_against:
        row["consumeOnAttackAgainst"] = True
    if effect.expires_after_source_turns is not None:
        row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
    if effect.expires_at_start_of_source_turn:
        row["expiresAtStartOfSourceTurn"] = True
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
    if action.source:
        row["source"] = action.source
    return row


def _spell_attack(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
        "range": action.range_ft, "attackBonus": action.attack_bonus,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type,
        "attackCount": action.attack_count, "attacksPerSlotAbove": action.attacks_per_slot_above,
        "upcastDicePerLevel": action.upcast_dice_per_level,
        "matchingDiceLeapRangeFt": action.matching_dice_leap_range_ft,
        "onHitModifierEffects": [_modifier_effect(effect) for effect in action.on_hit_modifier_effects],
        "animation": action.animation,
    }
    if action.source:
        row["source"] = action.source
    return row


def _healing(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "range": action.range_ft, "targetMode": action.target_mode, "maxTargets": action.max_targets,
            "areaRadiusFt": action.area_radius_ft, "diceCount": action.dice_count, "diceSize": action.dice_size,
            "healingBonus": action.healing_bonus, "restoreToEffectiveMax": action.restore_to_effective_max,
            "healingFromResourcePool": action.healing_from_resource_pool,
            "percentileSuccessMax": action.percentile_success_max, "resourceId": action.resource_id,
            "resourceCost": action.resource_cost, "excludedCreatureTypes": list(action.excluded_creature_types),
            "removableConditions": list(action.removable_conditions),
            "proneReactionStand": action.prone_reaction_stand,
            "secondaryTargetWithinFt": action.secondary_target_within_ft,
            "grantsTemporaryHp": action.grants_temporary_hp,
            "sharedHealingPool": action.shared_healing_pool,
            "stabilizeAtZero": action.stabilize_at_zero,
            "animation": action.animation,
        }
    except Exception:
        logger.exception("Failed to serialize healing action %s.", action.id)
        raise


def persistent_hazard_row(action: Any) -> dict[str, Any]:
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


def persistent_barrier_row(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "castRangeFt": action.cast_range_ft,
            "concentration": action.concentration, "durationRounds": action.duration_rounds,
            "permanentAfterFullDuration": action.permanent_after_full_duration,
            "minSections": action.min_sections, "maxSections": action.max_sections,
            "sectionsMustBeContiguous": action.sections_must_be_contiguous, "sectionLengthFt": action.section_length_ft,
            "sectionHeightFt": action.section_height_ft,
            "sectionThicknessInches": action.section_thickness_inches,
            "armorClass": action.armor_class, "hitPointsPerSection": action.hit_points_per_section,
            "damageImmunities": list(action.damage_immunities),
            "blocksMovement": action.blocks_movement,
            "blocksLineOfSight": action.blocks_line_of_sight,
            "material": action.material, "requiredSupportMaterial": action.required_support_material,
            "animation": action.animation, "source": action.source,
        }
    except Exception:
        logger.exception("Failed to serialize persistent barrier %s.", action.id)
        raise


def persistent_beneficial_zone_row(action: Any) -> dict[str, Any]:
    try:
        return {
            "id": action.id, "name": action.name, "actionCost": action.action_cost,
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "castRangeFt": action.cast_range_ft, "durationRounds": action.duration_rounds,
            "shape": action.shape, "lengthFt": action.length_ft,
            "moveActionCost": action.move_action_cost, "moveDistanceFt": action.move_distance_ft,
            "moveRangeFt": action.move_range_ft,
            "armorClassBonus": action.armor_class_bonus,
            "coverBonus": action.cover_bonus,
            "savingThrowBonus": action.saving_throw_bonus,
            "savingThrowAbilities": list(action.saving_throw_abilities),
            "allyDamageResistances": list(action.ally_damage_resistances),
            "includeSourceForDefense": action.include_source_for_defense,
            "endIfSourceIncapacitated": action.end_if_source_incapacitated,
            "endIfSourceDead": action.end_if_source_dead,
            "animation": action.animation, "source": action.source,
        }
    except Exception:
        logger.exception("Failed to serialize persistent beneficial zone %s.", action.id)
        raise


def defense_row(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost,
        "range": action.range_ft, "durationMinutes": action.duration_minutes,
        "targetPolicy": action.target_policy, "targetCount": action.target_count,
        "targetAllLegal": action.target_all_legal,
        "temporaryHp": action.temporary_hp,
        "temporaryHpPerSlotAbove": action.temporary_hp_per_slot_above,
        "damageResistances": list(action.damage_resistances),
        "conditionIds": list(action.condition_ids),
        "modifierEffects": [_modifier_effect(effect) for effect in action.modifier_effects],
        "concentration": action.concentration,
        "priority": action.priority, "animation": action.animation,
    }
    if action.free_opening_cast:
        row["freeOpeningCast"] = True
    if action.movement_mode_grants:
        row["movementModeGrants"] = [
            {
                "mode": grant.mode,
                "fixedSpeedFt": grant.fixed_speed_ft,
                "matchCurrentSpeed": grant.match_current_speed,
            }
            for grant in action.movement_mode_grants
        ]
    if action.max_hp_increase:
        row["maxHpIncrease"] = action.max_hp_increase
    if action.current_hp_increase:
        row["currentHpIncrease"] = action.current_hp_increase
    if action.source:
        row["source"] = action.source
    if action.selectable_resistance_types:
        row["selectableResistanceTypes"] = list(action.selectable_resistance_types)
    if action.share_damage_with_source:
        row["shareDamageWithSource"] = True
        row["shareRangeFt"] = action.share_range_ft
    return row


def targeted_concentration_damage_row(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "level": action.level,
        "actionCost": action.action_cost, "range": action.range_ft,
        "diceCount": action.dice_count, "diceSize": action.dice_size,
        "damageType": action.damage_type,
        "durationRoundsBySlot": dict(action.duration_rounds_by_slot),
        "retargetAfterTargetZero": action.retarget_after_target_zero,
        "freeCastResourceId": action.free_cast_resource_id,
        "freeCastResourceCost": action.free_cast_resource_cost,
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

def _attack_action_weapon_buff(action: Any) -> dict[str, Any]:
    return {
        "id": action.id,
        "name": action.name,
        "resourceId": action.resource_id,
        "resourceCost": action.resource_cost,
        "weaponId": action.weapon_id,
        "durationRounds": action.duration_rounds,
        "attackRollBonus": action.attack_roll_bonus,
        "damageTypeChoice": _value(action.damage_type_choice) if action.damage_type_choice is not None else None,
        "sourceIsMagical": action.source_is_magical,
        "animation": action.animation,
    }


def _suppression_zone(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "castRangeFt": action.cast_range_ft,
            "radiusFt": action.radius_ft, "durationRounds": action.duration_rounds,
            "concentration": action.concentration, "deafens": action.deafens,
            "blocksVerbalSpells": action.blocks_verbal_spells,
            "thunderImmunity": action.thunder_immunity,
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
        }
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize suppression zone %s.", action.id)
        raise


def _save_zone(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "castRangeFt": action.cast_range_ft,
            "radiusFt": action.radius_ft, "durationRounds": action.duration_rounds,
            "concentration": action.concentration, "saveAbility": action.save_ability,
            "dc": action.dc, "triggers": list(action.triggers),
            "saveTriggers": list(action.save_triggers),
            "oncePerTurn": action.once_per_turn,
            "damageDiceCount": action.damage_dice_count,
            "damageDiceSize": action.damage_dice_size,
            "damageType": action.damage_type, "successDamage": action.success_damage,
            "upcastDicePerLevel": action.upcast_dice_per_level,
            "failedSaveConditionId": action.failed_save_condition_id,
            "failedSaveDurationRounds": action.failed_save_duration_rounds,
            "failedSaveSuppressAction": action.failed_save_suppress_action,
            "failedSaveSuppressBonusAction": action.failed_save_suppress_bonus_action,
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
        }
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize save zone %s.", action.id)
        raise


def _teleport(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "passengerCount": action.passenger_count, "passengerRangeFt": action.passenger_range_ft,
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
        }
        if action.source:
            row["source"] = action.source
        return row
    except Exception:
        logger.exception("Failed to serialize teleport action %s.", action.id)
        raise


def _timed_self_buff(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost,
        "activationTiming": action.activation_timing,
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
    if action.friendly_cover_aura is not None:
        row["friendlyCoverAura"] = action.friendly_cover_aura.model_dump(mode="json")
    if action.hostile_start_turn_condition_aura is not None:
        row["hostileStartTurnConditionAura"] = action.hostile_start_turn_condition_aura.model_dump(mode="json")
    if action.concentration:
        row["concentration"] = True
    if action.modifier_effects:
        row["modifierEffects"] = [_modifier_effect(effect) for effect in action.modifier_effects]
    if action.start_turn_emanation_damage is not None:
        row["startTurnEmanationDamage"] = action.start_turn_emanation_damage.model_dump(mode="json")
    if action.emitted_environment_contexts:
        row["emittedEnvironmentContexts"] = [
            item.model_dump(mode="json") for item in action.emitted_environment_contexts
        ]
    if action.melee_hit_retaliation is not None:
        row["meleeHitRetaliation"] = {
            "rangeFt": action.melee_hit_retaliation.range_ft,
            "diceCount": action.melee_hit_retaliation.dice_count,
            "diceSize": action.melee_hit_retaliation.dice_size,
            "damageType": _value(action.melee_hit_retaliation.damage_type),
        }
    return row


def _removal(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
        "targetMode": action.target_mode, "removableConditions": list(action.removable_conditions),
        "excludedCreatureTypes": list(action.excluded_creature_types),
        "maxConditionsPerUse": action.max_conditions_per_use, "resourceCosts": dict(action.resource_costs),
        "resourceCostsPerCondition": dict(action.resource_costs_per_condition),
        "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
    }
    if action.reaction_trigger:
        row["reactionTrigger"] = action.reaction_trigger
    if action.reduces_exhaustion_levels:
        row["reducesExhaustionLevels"] = action.reduces_exhaustion_levels
    if action.removes_curses:
        row["removesCurses"] = True
    if action.removes_all_curses:
        row["removesAllCurses"] = True
    if action.removes_ability_score_reductions:
        row["removesAbilityScoreReductions"] = True
    if action.removes_hit_point_maximum_reductions:
        row["removesHitPointMaximumReductions"] = True
    if action.requires_active_effect_id:
        row["requiresActiveEffectId"] = action.requires_active_effect_id
    if action.ends_required_effect:
        row["endsRequiredEffect"] = True
    return row


def _progression_features(template: CombatantTemplate) -> dict[str, Any]:
    features = template.progression_features
    row: dict[str, Any] = {}
    if features.critical_hit_minimum != 20:
        row["critical_hit_minimum"] = features.critical_hit_minimum
    if features.initiative_advantage:
        row["initiative_advantage"] = True
    if features.first_round_extra_turn_grants:
        row["first_round_extra_turn_grants"] = [item.model_dump() for item in features.first_round_extra_turn_grants]
    if features.first_round_extra_turn_initiative_offset is not None:
        row["first_round_extra_turn_initiative_offset"] = features.first_round_extra_turn_initiative_offset
    if features.suppress_attack_advantage_while_not_incapacitated:
        row["suppress_attack_advantage_while_not_incapacitated"] = True
    if features.ignore_unseen_target_attack_disadvantage:
        row["ignore_unseen_target_attack_disadvantage"] = True
    if features.miss_to_hit_override_resource_id:
        row["miss_to_hit_override_resource_id"] = features.miss_to_hit_override_resource_id
    if features.miss_to_hit_override_source_name:
        row["miss_to_hit_override_source_name"] = features.miss_to_hit_override_source_name
    if features.failed_save_reroll_grants:
        row["failed_save_reroll_grants"] = [
            item.model_dump(exclude_unset=True, exclude_none=True)
            for item in features.failed_save_reroll_grants
        ]
    if features.failed_d20_test_override_grants:
        row["failed_d20_test_override_grants"] = [
            item.model_dump() for item in features.failed_d20_test_override_grants
        ]
    if features.resource_backed_d20_bonus_dice:
        row["resource_backed_d20_bonus_dice"] = [
            item.model_dump() for item in features.resource_backed_d20_bonus_dice
        ]
    if features.resource_backed_d20_outcome_adjustments:
        row["resource_backed_d20_outcome_adjustments"] = [
            item.model_dump(mode="json") for item in features.resource_backed_d20_outcome_adjustments
        ]
    if features.deferred_save_effect:
        row["deferred_save_effect"] = features.deferred_save_effect.model_dump()
    if features.source_reduces_hostile_to_zero_hp_temporary_hp:
        row["source_reduces_hostile_to_zero_hp_temporary_hp"] = (
            features.source_reduces_hostile_to_zero_hp_temporary_hp.model_dump(mode="json")
        )
    if features.source_damage_temporary_hp:
        row["source_damage_temporary_hp"] = features.source_damage_temporary_hp.model_dump(mode="json")
    if features.selectable_damage_resistance:
        row["selectable_damage_resistance"] = features.selectable_damage_resistance.model_dump(mode="json")
    if features.resource_backed_on_hit_exile:
        row["resource_backed_on_hit_exile"] = features.resource_backed_on_hit_exile.model_dump(mode="json")
    if features.resource_backed_on_hit_save_rider:
        row["resource_backed_on_hit_save_rider"] = features.resource_backed_on_hit_save_rider.model_dump(mode="json")
    if features.resource_backed_post_hit_damage:
        row["resource_backed_post_hit_damage"] = features.resource_backed_post_hit_damage.model_dump(mode="json")
    if features.delayed_resource_refill:
        row["delayed_resource_refill"] = features.delayed_resource_refill.model_dump(mode="json")
    if features.start_turn_resource_refill_ids:
        row["start_turn_resource_refill_ids"] = list(features.start_turn_resource_refill_ids)
    if features.alternate_spell_cast_grants:
        row["alternate_spell_cast_grants"] = [
            item.model_dump() for item in features.alternate_spell_cast_grants
        ]
    if features.opening_targeting_ward:
        row["opening_targeting_ward"] = features.opening_targeting_ward.model_dump()
    if features.once_per_turn_weapon_hit_damage_rider:
        row["once_per_turn_weapon_hit_damage_rider"] = features.once_per_turn_weapon_hit_damage_rider.model_dump()
    if features.once_per_turn_weapon_hit_damage_riders:
        row["once_per_turn_weapon_hit_damage_riders"] = [
            item.model_dump() for item in features.once_per_turn_weapon_hit_damage_riders
        ]
    if features.outgoing_healing_dice_maximizer:
        row["outgoing_healing_dice_maximizer"] = features.outgoing_healing_dice_maximizer.model_dump()
    if features.athletics_advantage:
        row["athletics_advantage"] = True
    if features.saving_throw_proficiency_grants:
        row["saving_throw_proficiency_grants"] = [
            item.model_dump() for item in features.saving_throw_proficiency_grants
        ]
    if features.saving_throw_advantage_grants:
        row["saving_throw_advantage_grants"] = [
            _save_advantage_grant(item) for item in features.saving_throw_advantage_grants
        ]
    if features.passive_debuff_counter_grants:
        row["passive_debuff_counter_grants"] = [
            item.model_dump(mode="json") for item in features.passive_debuff_counter_grants
        ]
    if features.bloodied_start_turn_heal_amount:
        row["bloodied_start_turn_heal_amount"] = features.bloodied_start_turn_heal_amount
    if features.death_save_advantage:
        row["death_save_advantage"] = True
    if features.death_save_recovery_minimum != 20:
        row["death_save_recovery_minimum"] = features.death_save_recovery_minimum
    if features.critical_move_fraction:
        row["critical_move_fraction"] = features.critical_move_fraction
    if features.rage_persists_without_maintenance:
        row["rage_persists_without_maintenance"] = True
    if features.cunning_action:
        row["cunning_action"] = True
    if features.sneak_attack_d6:
        row["sneak_attack_d6"] = features.sneak_attack_d6
    if features.cunning_strike_obscure_die_cost:
        row["cunning_strike_obscure_die_cost"] = features.cunning_strike_obscure_die_cost
    return row



def _bonus_attack_grant(item: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": item.id,
        "name": item.name,
        "attackIds": list(item.attack_ids),
        "attackCount": item.attack_count,
        "trigger": item.trigger,
        "resourceId": item.resource_id,
        "resourceCost": item.resource_cost,
        "priority": item.priority,
    }
    if item.on_hit_condition_save is not None:
        effect = item.on_hit_condition_save
        save_row: dict[str, Any] = {
            "saveAbility": effect.save_ability,
            "dc": effect.dc,
            "conditionId": effect.condition_id,
            "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
        }
        if effect.duration_rounds is not None:
            save_row["durationRounds"] = effect.duration_rounds
        if effect.repeat_save_timing is not None:
            save_row["repeatSaveTiming"] = _value(effect.repeat_save_timing)
        if effect.repeat_save_failure_condition_id:
            save_row["repeatSaveFailureConditionId"] = effect.repeat_save_failure_condition_id
        if effect.failure_push_ft:
            save_row["failurePushFt"] = effect.failure_push_ft
        if effect.excluded_creature_types:
            save_row["excludedCreatureTypes"] = list(effect.excluded_creature_types)
        if effect.excluded_creature_subtypes:
            save_row["excludedCreatureSubtypes"] = list(effect.excluded_creature_subtypes)
        row["onHitConditionSave"] = save_row
    return row

def template_row(template: CombatantTemplate) -> dict[str, Any]:
    try:
        traits = {item.value for item in template.combat_traits}
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        row: dict[str, Any] = {
            "id": template.id, "name": template.name, "archetype": template.archetype,
            "level": template.level, "challenge_rating": template.challenge_rating, "kind": template.kind,
            "ruleset": template.ruleset, "size": template.size.value,
            "ability_scores": template.ability_scores.model_dump() if template.ability_scores else None,
            "armor_class": template.armor_class, "max_hp": template.max_hp,
            "speed_ft": template.speed_ft, "movement_modes": template.movement_modes.model_dump(),
            "initiative_bonus": template.initiative_bonus,
        "blindsight_ft": template.blindsight_ft, "truesight_ft": template.truesight_ft,
            "saving_throw_bonuses": template.saving_throw_bonuses, "skill_bonuses": template.skill_bonuses,
            "attacks": [attack_row(item, traits) for item in attacks], "primary_attack_id": template.weapon_attack.id,
            "saving_throw_actions": [_save(item) for item in template.saving_throw_actions],
            "hp_threshold_condition_actions": [
                {
                    "id": item.id, "name": item.name, "actionCost": item.action_cost,
                    "range": item.range_ft, "maxCurrentHp": item.max_current_hp,
                    "requiresTargetSight": item.requires_target_sight,
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
                    "requiresTargetSight": item.requires_target_sight,
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
            "traits": sorted(traits), "resources": {item.id: item.max_uses for item in template.resources},
            "damage_resistances": [item.value for item in template.damage_resistances],
            "damage_vulnerabilities": [item.value for item in template.damage_vulnerabilities],
            "damage_immunities": [item.value for item in template.damage_immunities],
            "conditional_damage_defenses": [
                {
                    "id": item.id, "kind": _value(item.kind),
                    "damageTypes": [_value(kind) for kind in item.damage_types],
                    "requiredSourceQualifiers": [_value(kind) for kind in item.required_source_qualifiers],
                    "forbiddenSourceQualifiers": [_value(kind) for kind in item.forbidden_source_qualifiers],
                }
                for item in template.conditional_damage_defenses
            ],
            "condition_immunities": list(template.condition_immunities),
            "terminal_effect_tags": list(template.terminal_effect_tags),
            "effect_tag_condition_grants": [grant.model_dump(mode="json") for grant in template.effect_tag_condition_grants],
            "wearing_metal_armor": template.wearing_metal_armor,
            "passive_modifier_grants": [_passive_modifier_grant(item) for item in template.passive_modifier_grants],
            "visual": {"armor": template.visual.armor, "main_hand": template.visual.main_hand,
                       "off_hand": template.visual.off_hand, "body_style": template.visual.body_style},
            "source": template.source, **_progression_features(template),
        }
        if template.damage_absorptions:
            row["damage_absorptions"] = [
                {"sourceId": item.source_id, "sourceName": item.source_name, "damageType": _value(item.damage_type)}
                for item in template.damage_absorptions
            ]
        if template.support_action_modes:
            row["support_action_modes"] = list(template.support_action_modes)
        if template.environment_context_reactions:
            row["environment_context_reactions"] = [
                item.model_dump(mode="json") for item in template.environment_context_reactions
            ]
        if template.kind == "monster":
            row["creature_type"] = template.creature_type
            row["source_trait_names"] = list(template.source_trait_names)
            row["source_reaction_names"] = list(template.source_reaction_names)
            row["source_bonus_action_names"] = list(template.source_bonus_action_names)
            row["source_limited_use_names"] = list(template.source_limited_use_names)
            row["source_legendary_action_names"] = list(template.source_legendary_action_names)
            row["source_spellcasting_fingerprint"] = template.source_spellcasting_fingerprint
        if template.initiative_resource_refill_grants:
            row["initiative_resource_refill_grants"] = [
                {
                    key: value
                    for key, value in item.model_dump().items()
                    if (key != "restore_to_minimum" or value is not None)
                    and (key != "healing_rider" or value is not None)
                } for item in template.initiative_resource_refill_grants
            ]
        if template.bonus_attack_grants:
            row["bonusAttackGrants"] = [_bonus_attack_grant(item) for item in template.bonus_attack_grants]
        if template.bonus_tactical_action_grants:
            row["bonusTacticalActionGrants"] = [
                {
                    "id": item.id, "name": item.name, "effects": list(item.effects),
                    "resourceId": item.resource_id, "resourceCost": item.resource_cost,
                    "priority": item.priority, "usePolicy": item.use_policy,
                    "jumpDistanceMultiplier": item.jump_distance_multiplier,
                }
                for item in template.bonus_tactical_action_grants
            ]
        if template.resource_conversion_actions:
            row["resource_conversion_actions"] = [
                {
                    "id": item.id, "name": item.name, "actionCost": item.action_cost,
                    "sourceResourceId": item.source_resource_id, "sourceCost": item.source_cost,
                    "sourceReserve": item.source_reserve,
                    "additionalSourceCosts": dict(item.additional_source_costs),
                    "requiresTargetEmpty": item.requires_target_empty, "oncePerTurn": item.once_per_turn,
                    "oncePerTurnGroup": item.once_per_turn_group,
                    "targetResourceId": item.target_resource_id, "targetGain": item.target_gain,
                    "targetAllowsOverflow": item.target_allows_overflow,
                    "automation": item.automation, "priority": item.priority, "source": item.source,
                }
                for item in template.resource_conversion_actions
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
        recharge = recharge_rows(template)
        if recharge:
            row["recharge_rules"] = recharge
        if template.attack_damage_reduction_reaction:
            rule = template.attack_damage_reduction_reaction
            row["attackDamageReductionReaction"] = {
                "sourceId": rule.source_id,
                "sourceName": rule.source_name,
                "attackKinds": list(rule.attack_kinds),
                "requiredDamageTypes": [item.value for item in rule.required_damage_types],
                "reductionDiceCount": rule.reduction_dice_count,
                "reductionDiceSize": rule.reduction_dice_size,
                "reductionAbility": rule.reduction_ability,
                "addLevel": rule.add_level,
                **(
                    {"zeroDamageRedirect": {
                        "sourceId": rule.zero_damage_redirect.source_id,
                        "sourceName": rule.zero_damage_redirect.source_name,
                        "resourceId": rule.zero_damage_redirect.resource_id,
                        "resourceCost": rule.zero_damage_redirect.resource_cost,
                        "meleeRangeFt": rule.zero_damage_redirect.melee_range_ft,
                        "rangedRangeFt": rule.zero_damage_redirect.ranged_range_ft,
                        "saveAbility": rule.zero_damage_redirect.save_ability,
                        "saveDc": rule.zero_damage_redirect.save_dc,
                        "damageDiceCount": rule.zero_damage_redirect.damage_dice_count,
                        "damageDiceSize": rule.zero_damage_redirect.damage_dice_size,
                        "damageBonusAbility": rule.zero_damage_redirect.damage_bonus_ability,
                        "requiresSight": rule.zero_damage_redirect.requires_sight,
                        "requiresClearLine": rule.zero_damage_redirect.requires_clear_line,
                    }} if rule.zero_damage_redirect else {}
                ),
            }
        if template.parry_reaction:
            row["parry_reaction"] = {"ac_bonus": template.parry_reaction.ac_bonus}
        if template.redirect_attack_reaction:
            row["redirect_attack_reaction"] = {
                "ally_range_ft": template.redirect_attack_reaction.ally_range_ft,
                "ally_max_size": template.redirect_attack_reaction.ally_max_size.value,
            }
        if template.spell_save_actions:
            row["spell_save_actions"] = [_spell(item) for item in template.spell_save_actions]
        if template.spell_attack_actions:
            row["spell_attack_actions"] = [_spell_attack(item) for item in template.spell_attack_actions]
        if template.targeted_concentration_damage_actions:
            row["targeted_concentration_damage_actions"] = [
                targeted_concentration_damage_row(item) for item in template.targeted_concentration_damage_actions
            ]
        if template.auto_hit_spell_actions:
            row["auto_hit_spell_actions"] = [_auto_hit_spell(item) for item in template.auto_hit_spell_actions]
        if template.spell_cast_timed_resistances:
            row["spellCastTimedResistances"] = [
                {
                    "id": item.id, "name": item.name,
                    "qualifyingDamageType": item.qualifying_damage_type.value,
                    "resistanceDamageType": item.resistance_damage_type.value,
                    "resourceId": item.resource_id, "resourceCost": item.resource_cost,
                    "durationRounds": item.duration_rounds, "priority": item.priority,
                }
                for item in template.spell_cast_timed_resistances
            ]
        if template.defensive_spell_actions:
            row["defensive_spell_actions"] = [defense_row(item) for item in template.defensive_spell_actions]
        if template.healing_actions:
            row["healingActions"] = [_healing(item) for item in template.healing_actions]
        if template.d20_bonus_die_actions:
            row["d20BonusDieActions"] = [_d20_bonus_die_action(item) for item in template.d20_bonus_die_actions]
        if template.reaction_roll_penalty_actions:
            row["reactionRollPenaltyActions"] = [_reaction_roll_penalty(item) for item in template.reaction_roll_penalty_actions]
        if template.persistent_hazard_actions:
            row["persistent_hazard_actions"] = [
                persistent_hazard_row(item) for item in template.persistent_hazard_actions
            ]
        if template.persistent_barrier_actions:
            row["persistent_barrier_actions"] = [
                persistent_barrier_row(item) for item in template.persistent_barrier_actions
            ]
        if template.persistent_beneficial_zone_actions:
            row["persistent_beneficial_zone_actions"] = [
                persistent_beneficial_zone_row(item) for item in template.persistent_beneficial_zone_actions
            ]
        if template.condition_removal_actions:
            row["condition_removal_actions"] = [_removal(item) for item in template.condition_removal_actions]
        if template.timed_self_buff_actions:
            row["timed_self_buff_actions"] = [_timed_self_buff(item) for item in template.timed_self_buff_actions]
        if template.suppression_zone_actions:
            row["suppression_zone_actions"] = [_suppression_zone(item) for item in template.suppression_zone_actions]
        if template.persistent_save_zone_actions:
            row["persistent_save_zone_actions"] = [_save_zone(item) for item in template.persistent_save_zone_actions]
        if template.teleport_actions:
            row["teleport_actions"] = [_teleport(item) for item in template.teleport_actions]
        if template.attack_action_weapon_buffs:
            row["attack_action_weapon_buffs"] = [
                _attack_action_weapon_buff(item) for item in template.attack_action_weapon_buffs
            ]
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
                    "endsOnIncapacitated": item.ends_on_incapacitated,
                    "replaceExistingForm": item.replace_existing_form,
                    "retainSpellcasting": item.retain_spellcasting,
                **({"retainedSpellActionIds": list(item.retained_spell_action_ids)} if item.retained_spell_action_ids else {}),
                    "setupSpellId": item.setup_spell_id,
                    "source": item.source,
                }
                for item in template.replacement_form_actions
            ]
        if template.concentration_repeat_save_actions:
            row["concentration_repeat_save_actions"] = [
                {
                    "id": item.id,
                    "name": item.name,
                    "sourceSpellId": item.source_spell_id,
                    "actionCost": item.action_cost,
                    "priority": item.priority,
                    "animation": item.animation,
                    "source": item.source,
                }
                for item in template.concentration_repeat_save_actions
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
            row["attack_action"] = {"id": template.attack_action.id, "name": template.attack_action.name, "slots": [
                {"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
                for slot in template.attack_action.slots
            ]}
        if template.attack_action and template.attack_action.variants:
            row["attack_action"]["variants"] = [
                {"id": variant.id, "attackKind": _value(variant.attack_kind) if variant.attack_kind else None,
                 "slots": [{"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
                           for slot in variant.slots]}
                for variant in template.attack_action.variants
            ]
        if template.regeneration is not None:
            row["regeneration"] = template.regeneration.model_dump(mode="json")
        if template.damage_threshold_zero_hp_replacements:
            row["damage_threshold_zero_hp_replacements"] = [
                item.model_dump(mode="json") for item in template.damage_threshold_zero_hp_replacements
            ]
        if template.triggered_extra_attack_stacks:
            row["triggered_extra_attack_stacks"] = [
                {
                    "sourceId": item.source_id,
                    "sourceName": item.source_name,
                    "triggerDamageType": item.trigger_damage_type.value,
                    "triggerDamageMinimum": item.trigger_damage_minimum,
                    "requiresBloodied": item.requires_bloodied,
                    "maxStacks": item.max_stacks,
                    "maxUses": item.max_uses,
                    "exhaustionPerStack": item.exhaustion_per_stack,
                    "attack": attack_row(item.attack, set()),
                    "clearsOnRegenerationHeal": item.clears_on_regeneration_heal,
                }
                for item in template.triggered_extra_attack_stacks
            ]
        if template.legendary_actions:
            row["legendary_actions"] = [item.model_dump(mode="json") for item in template.legendary_actions]
        if template.save_success_overrides:
            row["save_success_overrides"] = [
                item.model_dump(mode="json") for item in template.save_success_overrides
            ]
        return row
    except Exception:
        logger.exception("Failed to serialize combatant template %s.", template.id)
        raise
