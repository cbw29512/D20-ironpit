from __future__ import annotations

import json
import logging
from pathlib import Path

from app.combat.charge_profiles import charge_profile_for_attack
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-2014.js"


def _add_charge_follow_up_metadata(template, row: dict[str, object]) -> None:
    browser_attacks = {attack["id"]: attack for attack in row["attacks"]}
    attacks = [attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks] if attack is not None]
    for attack in attacks:
        profile = charge_profile_for_attack(attack)
        if profile is None or profile.follow_up_attack_id is None:
            continue
        charge = browser_attacks[attack.id].get("charge")
        if not isinstance(charge, dict):
            raise RuntimeError(f"Charge follow-up metadata requires serialized Charge profile for {attack.id}.")
        if profile.follow_up_required_target_condition is not None:
            charge["followUpRequiredTargetCondition"] = profile.follow_up_required_target_condition
        if profile.follow_up_action_cost != "free":
            charge["followUpActionCost"] = profile.follow_up_action_cost


def render() -> str:
    try:
        templates = build_basic_2014_monsters()
        rows = []
        for template in templates:
            row = template_row(template)
            _add_charge_follow_up_metadata(template, row)
            rows.append(row)
        ids = {row["id"] for row in rows}
        # Derive the expected count from the same immutable source classifier.
        # A newly admitted monster must not require a manually maintained constant.
        source_rows = load_monster_source_2014()
        expected_ids = {item.id for item in source_rows if not basic_blockers_2014(item)}
        if len(rows) != len(ids) or ids != expected_ids:
            raise RuntimeError(
                f"2014 browser roster mismatch: source admits {len(expected_ids)}, "
                f"exported {len(rows)} rows and {len(ids)} unique ids."
            )
        if any(row.get("ruleset") != "2014" or row.get("kind") != "monster" for row in rows):
            raise RuntimeError("2014 browser export contains a non-2014 monster.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from the certified isolated 2014 basic monster roster. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const monsters = {payload};\n"
            "  window.IRON_PIT_BROWSER_MONSTERS_2014 = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_2014_MVP_READY = true;\n"
            "})();\n"
        )
    except Exception:
        logger.exception("2014 browser monster rendering failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified 2014 browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("2014 browser monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
