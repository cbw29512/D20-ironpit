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


def _area_row(area):
    if area is None:
        return None
    row = {"shape": area.shape, "origin": area.origin}
    if area.radius_ft is not None: row["radiusFt"] = area.radius_ft
    if area.length_ft is not None: row["lengthFt"] = area.length_ft
    if area.width_ft is not None: row["widthFt"] = area.width_ft
    return row


def _policy_row(policy):
    if policy is None:
        return None
    return {
        "distinctAttackIds": policy.distinct_attack_ids,
        "repeatSlotIndex": policy.repeat_slot_index,
        "repeatDiceCount": policy.repeat_dice_count,
        "repeatDiceSize": policy.repeat_dice_size,
        "requiresPreviousHitSlots": list(policy.requires_previous_hit_slots),
        "sameTargetAsPreviousSlots": list(policy.same_target_as_previous_slots),
    }


def _attach_source_fingerprint(row, template) -> None:
    """Preserve source-audit metadata required by browser certification."""
    row["source_trait_names"] = list(template.source_trait_names)
    row["source_reaction_names"] = list(template.source_reaction_names)
    row["source_bonus_action_names"] = list(template.source_bonus_action_names)
    row["source_limited_use_names"] = list(template.source_limited_use_names)
    row["source_legendary_action_names"] = list(template.source_legendary_action_names)
    row["source_spellcasting_fingerprint"] = template.source_spellcasting_fingerprint
    if template.parry_reaction:
        row["parry_reaction"] = {"ac_bonus": template.parry_reaction.ac_bonus}
    if template.redirect_attack_reaction:
        row["redirect_attack_reaction"] = {
            "ally_range_ft": template.redirect_attack_reaction.ally_range_ft,
            "ally_max_size": template.redirect_attack_reaction.ally_max_size.value,
        }


def _attach_monster_actions(row, template) -> None:
    by_id = {action.id: action for action in template.saving_throw_actions}
    for action_row in row.get("saving_throw_actions", []):
        action = by_id.get(action_row["id"])
        if action is not None and action.area is not None:
            action_row["area"] = _area_row(action.area)
    if "Poor Depth Perception" in template.source_trait_names:
        for attack_row in row.get("attacks", []): attack_row["disadvantageBeyondFt"] = 30
    if template.attack_action and template.attack_action.policy:
        row.setdefault("attack_action", {})["policy"] = _policy_row(template.attack_action.policy)
    if template.zero_hp_prevention:
        row["zeroHpPrevention"] = {
            "resourceId": template.zero_hp_prevention.resource_id,
            "maxTriggerDamage": template.zero_hp_prevention.max_trigger_damage,
            "resultingHp": template.zero_hp_prevention.resulting_hp,
        }


def render() -> str:
    try:
        rows = []
        for template in _certified_monsters():
            row = template_row(template)
            row["creature_type"] = template.creature_type
            _attach_source_fingerprint(row, template)
            _attach_monster_actions(row, template)
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
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported canonical browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()