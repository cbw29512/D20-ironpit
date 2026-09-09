from __future__ import annotations

import logging
from typing import Any

from app.combat.charge import charge_profile_for_attack_id
from app.domain.models import CombatantTemplate, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _area(area: Any) -> dict[str, Any] | None:
    if area is None:
        return None
    row: dict[str, Any] = {"shape": area.shape}
    for source, target in (
        ("length_ft", "lengthFt"), ("width_ft", "widthFt"), ("radius_ft", "radiusFt"),
        ("height_ft", "heightFt"), ("origin_range_ft", "originRangeFt"),
    ):
        value = getattr(area, source)
        if value:
            row[target] = value
    return row


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
    if effect.forced_movement:
        row["forcedMovement"] = {
            "direction": effect.forced_movement.direction,
            "maxDistanceFt": effect.forced_movement.max_distance_ft,
            "distanceMode": effect.forced_movement.distance_mode,
        }
    return row or None


def _hit_modifier(effect: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"kind": effect.kind}
    if effect.flat_bonus:
        row["flatBonus"] = effect.flat_bonus
    if effect.consume_on_attack_against:
        row["consumeOnAttackAgainst"] = True
    if effect.consume_on_attack_made:
        row["consumeOnAttackMade"] = True
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
        if weapon.normal_range_ft is not None:
            row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
        if attack.fixed_damage is not None:
            row["fixedDamage"] = attack.fixed_damage
        if attack.resource_id:
            row["resourceId"] = attack.resource_id
            if attack.resource_cost != 1:
                row["resourceCost"] = attack.resource_cost
        if attack.rage_eligible:
            row["rageEligible"] = True
        if attack.knocks_prone_max_size is not None:
            row["proneMaxSize"] = attack.knocks_prone_max_size.value
        if attack.forbid_target_grappled_by_self:
            row["forbidSelfGrappledTarget"] = True
        if attack.conditional_attack_modifiers:
            row["conditionalAttackModifiers"] = [
                {"trigger": item.trigger, "mode": item.mode}
                for item in attack.conditional_attack_modifiers
            ]
        if attack.on_hit_damage:
            row["onHitDamage"] = [
                {"source": part.source, "diceCount": part.dice_count, "diceSize": part.dice_size,
                 "damageBonus": part.damage_bonus, "damageType": part.damage_type.value}
                for part in attack.on_hit_damage
            ]
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
            profile = charge_profile_for_attack_id(attack.id)
            if profile:
                charge: dict[str, Any] = {"minimumMove": profile.minimum_move_ft}
                if profile.prone_max_target_size is not None:
                    charge["proneMaxSize"] = profile.prone_max_target_size.value
                if profile.max_target_size is not None and profile.max_target_size != profile.prone_max_target_size:
                    charge["targetMaxSize"] = profile.max_target_size.value
                if profile.bonus_damage is not None:
                    charge.update(
                        diceCount=profile.bonus_damage.dice_count,
                        diceSize=profile.bonus_damage.dice_size,
                        damageType=profile.bonus_damage.damage_type.value,
                    )
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


def template_row(template: CombatantTemplate) -> dict[str, Any]:
    try:
        traits = {trait.value for trait in template.combat_traits}
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        row: dict[str, Any] = {
            "id": template.id, "name": template.name, "kind": template.kind, "archetype": template.archetype,
            "challenge_rating": template.challenge_rating, "size": template.size.value,
            "armor_class": template.armor_class, "max_hp": template.max_hp, "speed_ft": template.speed_ft,
            "movement_modes": template.movement_modes.model_dump(), "initiative_bonus": template.initiative_bonus,
            "attacks": [attack_row(attack, traits) for attack in attacks],
            "primary_attack_id": template.weapon_attack.id,
            "saving_throw_actions": [action.model_dump(mode="json") for action in template.saving_throw_actions],
            "traits": sorted(traits),
            "resources": {
                resource.id: {
                    "name": resource.name, "maxUses": resource.max_uses,
                    **({"rechargeD6Min": resource.recharge_d6_min} if resource.recharge_d6_min is not None else {}),
                }
                for resource in template.resources
            },
            "damage_resistances": sorted(item.value for item in template.damage_resistances),
            "damage_vulnerabilities": sorted(item.value for item in template.damage_vulnerabilities),
            "damage_immunities": sorted(item.value for item in template.damage_immunities),
            "condition_immunities": sorted(template.condition_immunities),
            "source_trait_names": list(template.source_trait_names),
            "source_reaction_names": list(template.source_reaction_names),
            "source_bonus_action_names": list(template.source_bonus_action_names),
            "source_limited_use_names": list(template.source_limited_use_names),
            "source_legendary_action_names": list(template.source_legendary_action_names),
            "source_spellcasting_fingerprint": template.source_spellcasting_fingerprint,
        }
        if template.attack_action is not None:
            row["attack_action"] = {
                "id": template.attack_action.id, "name": template.attack_action.name,
                "slots": [slot.model_dump(mode="json", by_alias=True) for slot in template.attack_action.slots],
            }
        return row
    except Exception:
        logger.exception("Failed to serialize template %s for browser runtime.", template.id)
        raise
