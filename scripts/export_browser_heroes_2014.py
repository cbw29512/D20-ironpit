from __future__ import annotations

import json
from pathlib import Path

from app.content.audited_fighter_2014 import build_certified_fighter_2014_levels

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-heroes-2014.js"


def _attack(attack):
    weapon = attack.weapon
    row = {
        "id": attack.id,
        "weaponId": weapon.id,
        "name": weapon.name,
        "kind": weapon.attack_kind.value,
        "bonus": attack.attack_bonus,
        "diceCount": weapon.dice_count,
        "diceSize": weapon.dice_size,
        "damageBonus": attack.damage_bonus,
        "damageType": weapon.damage_type.value,
        "reach": weapon.reach_ft,
        "animation": weapon.animation,
        "attackAbility": attack.attack_ability,
        "attackAbilityModifier": attack.attack_ability_modifier,
    }
    if weapon.normal_range_ft is not None:
        row.update(normal=weapon.normal_range_ft, long=weapon.long_range_ft, projectile=weapon.projectile)
    return row


def _template(template):
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    row = {
        "id": template.id,
        "class_id": "fighter",
        "build_id": "canonical-2014",
        "name": template.name,
        "archetype": template.archetype,
        "level": template.level,
        "kind": template.kind,
        "ruleset": template.ruleset,
        "size": template.size.value,
        "armor_class": template.armor_class,
        "max_hp": template.max_hp,
        "speed_ft": template.speed_ft,
        "initiative_bonus": template.initiative_bonus,
        "saving_throw_bonuses": template.saving_throw_bonuses,
        "skill_bonuses": template.skill_bonuses,
        "attacks": [_attack(item) for item in attacks],
        "primary_attack_id": template.weapon_attack.id,
        "resources": {item.id: item.max_uses for item in template.resources},
        "fighting_style": template.fighting_style,
        "fighting_styles": list(template.fighting_styles),
        "weapon_masteries": [],
        "critical_hit_minimum": template.progression_features.critical_hit_minimum,
        "source": template.source,
        "visual": {
            "armor": template.visual.armor,
            "main_hand": template.visual.main_hand,
            "off_hand": template.visual.off_hand,
            "body_style": template.visual.body_style,
            "figure_form": template.visual.body_style,
            "role": "fighter",
        },
    }
    if template.attack_action:
        row["attack_action"] = {
            "id": template.attack_action.id,
            "name": template.attack_action.name,
            "isAttackAction": template.attack_action.is_attack_action,
            "slots": [
                {"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
                for slot in template.attack_action.slots
            ],
        }
    return row


def render() -> str:
    rows = [_template(template) for template in build_certified_fighter_2014_levels()]
    payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    return (
        "/* GENERATED from the certified 2014 Champion Fighter source model. Do not hand-edit. */\n"
        "(() => {\n  \"use strict\";\n  const heroes = " + payload + ";\n"
        "  window.IRON_PIT_BROWSER_HEROES_2014 = Object.fromEntries(heroes.map((item) => [item.id, item]));\n"
        "})();\n"
    )


def main() -> None:
    DESTINATION.write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
