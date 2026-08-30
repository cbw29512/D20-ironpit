from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.content.certified_heroes import build_certified_hero_entries
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
    }


def _attack(attack: WeaponAttack) -> dict[str, Any]:
    if attack.conditional_damage:
        raise ValueError(f"Browser hero exporter has no certified conditional-damage mapping for {attack.id}.")
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
    control = _control(attack.control_effect)
    if control:
        row["controlEffect"] = control
    return row


def _save(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "saveAbility": action.save_ability, "dc": action.dc,
        "range": action.range_ft, "targetMaxSize": _value(action.target_max_size) if action.target_max_size else None,
        "damageDiceCount": action.damage_dice_count, "damageDiceSize": action.damage_dice_size,
        "damageBonus": action.damage_bonus, "damageType": action.damage_type, "successDamage": action.success_damage,
        "grappleEscapeDc": action.grapple_escape_dc, "restrainsWhileGrappled": action.restrains_while_grappled,
        "animation": action.animation,
    }


def _healing(action: Any) -> dict[str, Any]:
    return {
        "id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
        "targetMode": action.target_mode, "diceCount": action.dice_count, "diceSize": action.dice_size,
        "healingBonus": action.healing_bonus, "resourceId": action.resource_id,
        "resourceCost": action.resource_cost, "animation": action.animation,
    }


def _removal(action: Any) -> dict[str, Any]:
    row = {
        "id": action.id, "name": action.name, "actionCost": action.action_cost, "range": action.range_ft,
        "targetMode": action.target_mode, "removableConditions": list(action.removable_conditions),
        "maxConditionsPerUse": action.max_conditions_per_use, "resourceCosts": dict(action.resource_costs),
        "resourceCostsPerCondition": dict(action.resource_costs_per_condition), "animation": action.animation,
    }
    if action.reaction_trigger:
        row["reactionTrigger"] = action.reaction_trigger
    return row


def _template(key: tuple[str, int, str], template: CombatantTemplate) -> dict[str, Any]:
    class_id, _, build_id = key
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    row: dict[str, Any] = {
        "id": template.id, "class_id": class_id, "build_id": build_id, "name": template.name,
        "archetype": template.archetype, "level": template.level, "kind": template.kind, "size": template.size.value,
        "armor_class": template.armor_class, "max_hp": template.max_hp, "speed_ft": template.speed_ft,
        "initiative_bonus": template.initiative_bonus, "saving_throw_bonuses": template.saving_throw_bonuses,
        "skill_bonuses": template.skill_bonuses, "attacks": [_attack(item) for item in attacks],
        "primary_attack_id": template.weapon_attack.id,
        "saving_throw_actions": [_save(item) for item in template.saving_throw_actions],
        "healingActions": [_healing(item) for item in template.healing_actions],
        "condition_removal_actions": [_removal(item) for item in template.condition_removal_actions],
        "traits": [item.value for item in template.combat_traits],
        "resources": {item.id: item.max_uses for item in template.resources},
        "rage_damage_bonus": template.rage_damage_bonus, "wearing_heavy_armor": template.wearing_heavy_armor,
        "visual": {"armor": template.visual.armor, "main_hand": template.visual.main_hand,
                   "off_hand": template.visual.off_hand, "body_style": template.visual.body_style,
                   "figure_form": template.visual.body_style, "role": template.archetype.lower()},
        "source": template.source,
    }
    if template.attack_action:
        row["attack_action"] = {"id": template.attack_action.id, "name": template.attack_action.name, "slots": [
            {"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids} for slot in template.attack_action.slots
        ]}
    return row


def render() -> str:
    rows = [_template(key, template) for key, template in build_certified_hero_entries()]
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
