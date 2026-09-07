from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-generated.js"


def _certified_monsters():
    catalog = build_monster_catalog()
    ready_ids = {
        card.runnable_template_id
        for card in catalog
        if card.coverage_status is CoverageStatus.RAW_READY and card.runnable_template_id is not None
    }
    monsters = [template for template in build_arena_roster().monsters if template.id in ready_ids]
    if {template.id for template in monsters} != ready_ids:
        raise RuntimeError("RAW-ready catalog and canonical monster roster disagree.")
    return monsters


def _add_save_area_metadata(row, template) -> None:
    serialized = row.get("saving_throw_actions", [])
    if len(serialized) != len(template.saving_throw_actions):
        raise RuntimeError(f"Saving-throw serialization count drift for {template.id}.")
    for item, action in zip(serialized, template.saving_throw_actions, strict=True):
        # Preserve legacy canonical compatibility for the default action window.
        # Non-default costs remain explicit so bonus-action/reaction saves compose
        # through the same universal save runtime without a second subsystem.
        if action.action_cost == "action":
            item.pop("actionCost", None)
        if action.area is not None:
            area = {"shape": action.area.shape, "sizeFt": action.area.size_ft}
            if action.area.width_ft is not None:
                area["widthFt"] = action.area.width_ft
            item["area"] = area
        if action.additional_damage:
            item["additionalDamage"] = [
                {
                    "source": packet.source, "diceCount": packet.dice_count, "diceSize": packet.dice_size,
                    "damageBonus": packet.damage_bonus, "damageType": packet.damage_type.value,
                }
                for packet in action.additional_damage
            ]
        if action.failure_conditions:
            item["failureConditions"] = [
                {
                    "conditionId": effect.condition_id,
                    "expiryTiming": effect.expiry_timing,
                    "repeatSaveAbility": effect.repeat_save_ability,
                    "repeatSaveDc": effect.repeat_save_dc,
                    "repeatSaveTiming": effect.repeat_save_timing,
                    "allowedRemovalActionIds": list(effect.allowed_removal_action_ids),
                }
                for effect in action.failure_conditions
            ]


def _add_attack_resource_metadata(row, template) -> None:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    serialized = row.get("attacks", [])
    if len(serialized) != len(attacks):
        raise RuntimeError(f"Attack serialization count drift for {template.id}.")
    for item, attack in zip(serialized, attacks, strict=True):
        if attack.resource_id is not None:
            item["resourceId"] = attack.resource_id
            item["resourceCost"] = attack.resource_cost
        if attack.advantage_if_target_missing_hp:
            item["advantageIfTargetMissingHp"] = True
        if attack.max_hp_reduction is not None:
            rider = {}
            if attack.max_hp_reduction.damage_type is not None:
                rider["damageType"] = attack.max_hp_reduction.damage_type.value
            item["maxHpReduction"] = rider
        control = attack.control_effect
        if control is not None and control.grapple_escape_check_disadvantage:
            item.setdefault("controlEffect", {})["grappleEscapeCheckDisadvantage"] = True


def render() -> str:
    try:
        rows = []
        for template in _certified_monsters():
            row = template_row(template)
            _add_save_area_metadata(row, template)
            _add_attack_resource_metadata(row, template)
            row["creature_type"] = template.creature_type
            rows.append(row)
        ids = {row["id"] for row in rows}
        if len(rows) != len(ids):
            raise RuntimeError("Certified browser monster export contains duplicate template IDs.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from canonical Python RAW-ready monster templates. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const monsters = {payload};\n"
            "  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_CANONICAL_MONSTERS_READY = true;\n"
            "})();\n"
        )
    except Exception:
        logger.exception("Certified browser monster rendering failed.")
        raise


def main() -> None:
    try:
        content = render()
        DESTINATION.write_text(content, encoding="utf-8")
        logger.info("Exported canonical browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
