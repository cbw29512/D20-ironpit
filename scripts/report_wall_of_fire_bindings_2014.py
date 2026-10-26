"""Scan all 327 cards for source-declared Wall of Fire spell behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "WALL_OF_FIRE_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_persistent_save_zone_actions_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _save_zone


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "wall-of-fire"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple Wall of Fire source rows"})
            continue
        zones = [zone for zone in innate_persistent_save_zone_actions_2014(card) if zone.id == "wall-of-fire"]
        resources = {item.id: item for item in innate_spell_resources_2014(card)}
        expected_uses = int(declared[0].get("uses_per_day") or 0)
        if len(zones) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        zone = zones[0]
        resource = resources.get("wall-of-fire")
        if (
            zone.cast_range_ft != 120 or zone.radius_ft != 10 or zone.duration_rounds != 10
            or not zone.concentration or zone.save_ability != "dexterity"
            or zone.triggers != ["appear", "enter", "end_turn"]
            or zone.save_triggers != ["appear"] or zone.damage_dice_count != 5
            or zone.damage_dice_size != 8 or zone.damage_type != "fire"
            or zone.success_damage != "half" or zone.resource_id != "wall-of-fire"
            or resource is None or resource.max_uses != expected_uses
        ):
            exceptions.append({"monster": card.id, "reason": "compiled zone/resource lost source parameters"})
            continue
        python_wired.append(card.id)
        browser = _save_zone(zone)
        if (
            browser.get("id") == "wall-of-fire" and browser.get("dc") == zone.dc
            and browser.get("triggers") == ["appear", "enter", "end_turn"]
            and browser.get("resourceId") == "wall-of-fire"
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Wall of Fire semantics"})
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(python_wired),
        "wired_browser_card_count": len(browser_wired),
        "wired_cards": sorted(set(python_wired) & set(browser_wired)),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: explicit exceptions remain",
    }


def render() -> str:
    return json.dumps(report(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is stale; regenerate with this script.")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
