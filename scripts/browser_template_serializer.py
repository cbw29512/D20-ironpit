from __future__ import annotations

import logging
from typing import Any

from app.combat.charge import charge_profile_for_attack_id
from app.domain.models import CombatantTemplate, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _control(effect: Any) -> dict[str, Any] | None:
    if effect is None:
        return None
    row: dict[str, Any] = {}
    if effect.max_target_size: row["maxTargetSize"] = _value(effect.max_target_size)
    if effect.grapple_escape_dc is not None: row["grappleEscapeDc"] = effect.grapple_escape_dc
    if effect.restrains_while_grappled: row["restrainsWhileGrappled"] = True
    if effect.condition_id:
        row["conditionId"] = effect.condition_id
        if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
        if effect.expiry_timing: row["expiryTiming"] = effect.expiry_timing
        if effect.duration_rounds is not None: row["durationRounds"] = effect.duration_rounds
        if effect.repeat_save_ability:
            row["repeatSaveAbility"] = effect.repeat_save_ability; row["repeatSaveDc"] = effect.repeat_save_dc; row["repeatSaveTiming"] = effect.repeat_save_timing
        if effect.allowed_removal_action_ids: row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
        if effect.ends_on_damage: row["endsOnDamage"] = True
        if effect.source_effect_immunity_on_end: row["sourceEffectImmunityOnEnd"] = True
    return row or None


def _hit_modifier(effect: Any) -> dict[str, Any]:
    row = {"kind": effect.kind}
    if effect.flat_bonus: row["flatBonus"] = effect.flat_bonus
    if effect.consume_on_attack_against: row["consumeOnAttackAgainst"] = True
    if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
    if effect.expires_at_end_of_target_turn: row["expiresAtEndOfTargetTurn"] = True
    return row


def _charge(profile: Any) -> dict[str, Any]:
    row = {"minimumMove": profile.minimum_move_ft}
    prone_max = getattr(profile, "prone_max_target_size", None)
    target_max = getattr(profile, "max_target_size", None)
    prone_ability = getattr(profile, "prone_save_ability", None)
    prone_dc = getattr(profile, "prone_save_dc", None)
    bonus = getattr(profile, "bonus_damage", None)
    replacement = getattr(profile, "replacement_damage", None)
    follow_up = getattr(profile, "follow_up_attack_id", None)
    if prone_max is not None: row["proneMaxSize"] = _value(prone_max)
    if target_max is not None and target_max != prone_max: row["targetMaxSize"] = _value(target_max)
    if prone_ability is not None: row.update(proneSaveAbility=prone_ability, proneSaveDc=prone_dc)
    if bonus is not None: row.update(diceCount=bonus.dice_count, diceSize=bonus.dice_size, damageType=_value(bonus.damage_type))
    if replacement is not None:
        row["replacementDamage"] = {"diceCount": replacement.dice_count, "diceSize": replacement.dice_size,
                                    "damageBonus": replacement.damage_bonus, "damageType": _value(replacement.damage_type)}
    if follow_up: row["followUpAttackId"] = follow_up
    return row


def _failure_margin(spec: Any) -> dict[str, Any]:
    row = {"margin": spec.margin, "additionalConditionIds": list(spec.additional_condition_ids)}
    if spec.replacement_duration_rounds is not None: row["replacementDurationRounds"] = spec.replacement_duration_rounds
    if spec.replacement_duration_dice_count:
        row.update(
            replacementDurationDiceCount=spec.replacement_duration_dice_count,
            replacementDurationDiceSize=spec.replacement_duration_dice_size,
            replacementDurationRoundMultiplier=spec.replacement_duration_round_multiplier,
        )
    if spec.ends_on_damage: row["endsOnDamage"] = True
    if spec.allowed_removal_action_ids: row["allowedRemovalActionIds"] = list(spec.allowed_removal_action_ids)
    return row


def attack_row(attack: WeaponAttack, traits: set[str]) -> dict[str, Any]:
    try:
        weapon = attack.weapon
        row = {
            "id": attack.id, "name": weapon.name, "kind": weapon.attack_kind.value,
            "bonus": attack.attack_bonus, "diceCount": weapon.dice_count, "diceSize": weapon.dice_size,
            "damageBonus": attack.damage_bonus, "damageType": weapon.damage_type.value,
            "reach": weapon.reach_ft, "animation": weapon.animation,
        }
        if weapon.normal_range_ft is not None: row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
        if attack.fixed_damage is not None: row["fixedDamage"] = attack.fixed_damage
        if attack.rage_eligible: row["rageEligible"] = True
        if attack.knocks_prone_max_size is not None: row["proneMaxSize"] = attack.knocks_prone_max_size.value
        if attack.forbid_target_grappled_by_self: row["forbidSelfGrappledTarget"] = True
        if attack.grapple_target_policy != "normal": row["grappleTargetPolicy"] = attack.grapple_target_policy
        if attack.conditional_attack_advantage: row["conditionalAttackAdvantage"] = [{"trigger": spec.trigger} for spec in attack.conditional_attack_advantage]
        if attack.on_hit_damage:
            row["onHitDamage"] = [{"source": part.source, "diceCount": part.dice_count, "diceSize": part.dice_size, "damageBonus": part.damage_bonus, "damageType": part.damage_type.value} for part in attack.on_hit_damage]
        if attack.on_hit_modifier_effects: row["onHitModifiers"] = [_hit_modifier(effect) for effect in attack.on_hit_modifier_effects]
        if attack.on_hit_save_effect:
            effect = attack.on_hit_save_effect
            row["onHitSaveEffect"] = {"saveAbility": effect.save_ability, "dc": effect.dc, "conditionId": effect.condition_id}
            if effect.max_target_size is not None: row["onHitSaveEffect"]["maxTargetSize"] = effect.max_target_size.value
            if effect.duration_rounds is not None: row["onHitSaveEffect"]["durationRounds"] = effect.duration_rounds
            if effect.repeat_save_timing is not None: row["onHitSaveEffect"]["repeatSaveTiming"] = effect.repeat_save_timing
            if effect.repeat_save_failure_condition_id is not None: row["onHitSaveEffect"]["repeatSaveFailureConditionId"] = effect.repeat_save_failure_condition_id
            if effect.failure_margin_escalation is not None: row["onHitSaveEffect"]["failureMarginEscalation"] = _failure_margin(effect.failure_margin_escalation)
            if effect.ends_on_damage: row["onHitSaveEffect"]["endsOnDamage"] = True
            if effect.max_hp_reduction_equals_damage_taken: row["onHitSaveEffect"]["maxHpReductionEqualsDamageTaken"] = True
            if effect.zero_max_hp_kills: row["onHitSaveEffect"]["zeroMaxHpKills"] = True
            if effect.damage_dice_count:
                row["onHitSaveEffect"].update(
                    damageDiceCount=effect.damage_dice_count, damageDiceSize=effect.damage_dice_size,
                    damageBonus=effect.damage_bonus, damageType=effect.damage_type, successDamage=effect.success_damage,
                )
        if attack.conditional_damage:
            if len(attack.conditional_damage) != 1: raise ValueError(f"Browser supports one conditional damage rider on {attack.id}.")
            conditional = attack.conditional_damage[0]
            legacy = conditional.trigger == "attack_advantage" and conditional.mode == "add" and conditional.damage_bonus == 0 and conditional.damage_type == weapon.damage_type
            if legacy: row["conditionalAdvantage"] = [conditional.dice_count, conditional.dice_size]
            else:
                row["conditionalDamage"] = {"trigger": conditional.trigger, "mode": conditional.mode, "diceCount": conditional.dice_count, "diceSize": conditional.dice_size, "damageBonus": conditional.damage_bonus, "damageType": conditional.damage_type.value}
        control = _control(attack.control_effect)
        if control: row["controlEffect"] = control
        if CombatTrait.CHARGE.value in traits:
            profile = attack.charge_profile or charge_profile_for_attack_id(attack.id)
            if profile: row["charge"] = _charge(profile)
        return row
    except Exception:
        logger.exception("Failed to serialize attack %s for browser runtime.", attack.id); raise


def _save(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "saveAbility": action.save_ability, "dc": action.dc, "range": action.range_ft, "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size, "damageBonus": action.damage_bonus, "damageType": action.damage_type, "successDamage": action.success_damage, "animation": action.animation}
    if action.target_max_size: row["targetMaxSize"] = _value(action.target_max_size)
    if action.area: row["area"] = action.area.model_dump(exclude_none=True)
    if action.grapple_escape_dc is not None: row["grappleEscapeDc"] = action.grapple_escape_dc
    if action.restrains_while_grappled: row["restrainsWhileGrappled"] = True
    control = _control(action.failure_control_effect)
    if control: row["failureControlEffect"] = control
    if action.source_effect_immunity_on_success: row["sourceEffectImmunityOnSuccess"] = True
    if action.magical_effect: row["magicalEffect"] = True
    if action.resource_id: row["resourceId"] = action.resource_id; row["resourceCost"] = action.resource_cost
    return row


def _spell(action: Any) -> dict[str, Any]:
    row = {"id": action.id, "name": action.name, "level": action.level, "actionCost": action.action_cost, "range": action.range_ft, "saveAbility": action.save_ability, "dc": action.dc, "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size, "damageBonus": action.damage_bonus, "damageType": action.damage_type, "successDamage": action.success_damage, "upcastDicePerLevel": action.upcast_dice_per_level, "concentration": action.concentration, "animation": action.animation}
    if action.area_radius_ft is not None: row["areaRadius"] = action.area_radius_ft
    return row

