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
    return {
        "maxTargetSize": _value(effect.max_target_size) if effect.max_target_size else None,
        "grappleEscapeDc": effect.grapple_escape_dc,
        "restrainsWhileGrappled": effect.restrains_while_grappled,
        "conditionId": effect.condition_id,
        "expiresAtStartOfSourceTurn": effect.expires_at_start_of_source_turn,
    }


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
        if attack.rage_eligible:
            row["rageEligible"] = True
        if attack.knocks_prone_max_size is not None:
            row["proneMaxSize"] = attack.knocks_prone_max_size.value
        if attack.on_hit_damage:
            row["onHitDamage"] = [
                {"source": part.source, "diceCount": part.dice_count, "diceSize": part.dice_size,
                 "damageBonus": part.damage_bonus, "damageType": part.damage_type.value}
                for part in attack.on_hit_damage
            ]
        if attack.conditional_damage:
            if len(attack.conditional_damage) != 1:
                raise ValueError(f"Browser supports one conditional damage rider on {attack.id}.")
            conditional = attack.conditional_damage[0]
            if conditional.trigger != "attack_advantage" or conditional.damage_bonus != 0:
                raise ValueError(f"Unsupported browser conditional damage on {attack.id}.")
            if conditional.damage_type is not weapon.damage_type:
                raise ValueError(f"Conditional damage type differs from weapon type on {attack.id}.")
            row["conditionalAdvantage"] = [conditional.dice_count, conditional.dice_size]
        control = _control(attack.control_effect)
        if control:
            row["controlEffect"] = control
        if CombatTrait.CHARGE.value in traits:
            profile = charge_profile_for_attack_id(attack.id)
            if profile:
                row["charge"] = {
                    "minimumMove": profile.minimum_move_ft, "diceCount": profile.dice_count,
                    "diceSize": profile.dice_size, "damageType": profile.damage_type.value,
                    "proneMaxSize": profile.max_target_size.value,
                }
        return row
    except Exception:
        logger.exception("Failed to serialize attack %s for browser runtime.", attack.id)
        raise


def _save(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "saveAbility": action.save_ability, "dc": action.dc,
        "range": action.range_ft, "targetMaxSize": _value(action.target_max_size) if action.target_max_size else None,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type, "successDamage": action.success_damage,
        "grappleEscapeDc": action.grapple_escape_dc, "restrainsWhileGrappled": action.restrains_while_grappled,
        "animation": action.animation,
    }


def template_row(template: CombatantTemplate) -> dict[str, Any]:
    try:
        traits = {item.value for item in template.combat_traits}
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        row: dict[str, Any] = {
            "id": template.id, "name": template.name, "archetype": template.archetype,
            "level": template.level, "challenge_rating": template.challenge_rating, "kind": template.kind,
            "size": template.size.value, "armor_class": template.armor_class, "max_hp": template.max_hp,
            "speed_ft": template.speed_ft, "initiative_bonus": template.initiative_bonus,
            "saving_throw_bonuses": template.saving_throw_bonuses, "skill_bonuses": template.skill_bonuses,
            "attacks": [attack_row(item, traits) for item in attacks], "primary_attack_id": template.weapon_attack.id,
            "saving_throw_actions": [_save(item) for item in template.saving_throw_actions],
            "traits": sorted(traits), "resources": {item.id: item.max_uses for item in template.resources},
            "damage_resistances": [item.value for item in template.damage_resistances],
            "damage_vulnerabilities": [item.value for item in template.damage_vulnerabilities],
            "damage_immunities": [item.value for item in template.damage_immunities],
            "condition_immunities": list(template.condition_immunities),
            "visual": {"armor": template.visual.armor, "main_hand": template.visual.main_hand,
                       "off_hand": template.visual.off_hand, "body_style": template.visual.body_style},
            "source": template.source,
        }
        if template.attack_action:
            row["attack_action"] = {"id": template.attack_action.id, "name": template.attack_action.name, "slots": [
                {"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
                for slot in template.attack_action.slots
            ]}
        return row
    except Exception:
        logger.exception("Failed to serialize combatant template %s.", template.id)
        raise
