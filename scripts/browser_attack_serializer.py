from __future__ import annotations

import logging
from typing import Any

from app.domain.models import WeaponAttack
from browser_attack_effect_serializer import charge_row, control_row, hit_modifier_row

logger = logging.getLogger(__name__)


def attack_row(attack: WeaponAttack, traits: set[str]) -> dict[str, Any]:
    try:
        weapon = attack.weapon
        row: dict[str, Any] = {
            "id": attack.id,
            "name": weapon.name,
            "kind": weapon.attack_kind.value,
            "bonus": attack.attack_bonus,
            "diceCount": weapon.dice_count,
            "diceSize": weapon.dice_size,
            "damageBonus": attack.damage_bonus,
            "damageType": weapon.damage_type.value,
            "reach": weapon.reach_ft,
            "animation": weapon.animation,
        }
        if weapon.normal_range_ft is not None:
            row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
        if attack.resource_id is not None:
            row["resourceId"] = attack.resource_id
            row["resourceCost"] = attack.resource_cost
        if attack.fixed_damage is not None:
            row["fixedDamage"] = attack.fixed_damage
        if attack.rage_eligible:
            row["rageEligible"] = True
        if attack.knocks_prone_max_size is not None:
            row["proneMaxSize"] = attack.knocks_prone_max_size.value
        if attack.push_target_away_ft:
            row["pushTargetAwayFt"] = attack.push_target_away_ft
            if attack.push_target_max_size is not None:
                row["pushTargetMaxSize"] = attack.push_target_max_size.value
        if attack.pull_target_toward_ft:
            row["pullTargetTowardFt"] = attack.pull_target_toward_ft
            if attack.pull_target_max_size is not None:
                row["pullTargetMaxSize"] = attack.pull_target_max_size.value
        if attack.forbid_target_grappled_by_self:
            row["forbidSelfGrappledTarget"] = True
        if attack.conditional_attack_advantage:
            row["conditionalAttackAdvantage"] = [
                {"trigger": spec.trigger} for spec in attack.conditional_attack_advantage
            ]
        if attack.on_hit_damage:
            row["onHitDamage"] = [
                {
                    "source": part.source,
                    "diceCount": part.dice_count,
                    "diceSize": part.dice_size,
                    "damageBonus": part.damage_bonus,
                    "damageType": part.damage_type.value,
                }
                for part in attack.on_hit_damage
            ]
        if attack.on_hit_modifier_effects:
            row["onHitModifiers"] = [hit_modifier_row(effect) for effect in attack.on_hit_modifier_effects]
        if attack.conditional_damage:
            if len(attack.conditional_damage) != 1:
                raise ValueError(f"Browser supports one conditional damage rider on {attack.id}.")
            conditional = attack.conditional_damage[0]
            legacy = (
                conditional.trigger == "attack_advantage"
                and conditional.mode == "add"
                and conditional.damage_bonus == 0
                and conditional.damage_type == weapon.damage_type
            )
            if legacy:
                row["conditionalAdvantage"] = [conditional.dice_count, conditional.dice_size]
            else:
                row["conditionalDamage"] = {
                    "trigger": conditional.trigger,
                    "mode": conditional.mode,
                    "diceCount": conditional.dice_count,
                    "diceSize": conditional.dice_size,
                    "damageBonus": conditional.damage_bonus,
                    "damageType": conditional.damage_type.value,
                }
        control = control_row(attack.control_effect)
        if control:
            row["controlEffect"] = control
        charge = charge_row(attack.charge_profile)
        if charge:
            row["charge"] = charge
        return row
    except Exception:
        logger.exception("Failed to serialize attack %s for browser runtime.", attack.id)
        raise
