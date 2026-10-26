"""Scan all 327 cards for source-declared Hold Monster spell behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "HOLD_MONSTER_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _spell


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "hold-monster"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple Hold Monster source rows"})
            continue
        row = declared[0]
        actions = [action for action in innate_spell_save_actions_2014(card) if action.id == "hold-monster"]
        resources = {item.id: item for item in innate_spell_resources_2014(card)}
        if len(actions) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action = actions[0]
        rider = action.failed_save_timed_effect
        expected_uses = int(row.get("uses_per_day") or 0)
        resource = resources.get("hold-monster")
        if (
            action.dc <= 0 or action.range_ft != 90 or action.save_ability != "wisdom"
            or not action.requires_target_sight or action.excluded_target_creature_types != ["undead"]
            or rider is None or rider.effect_id != "paralyzed"
            or rider.repeat_save_timing != "target_turn_end"
            or resource is None or resource.max_uses != expected_uses
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action/resource lost source parameters"})
            continue
        python_wired.append(card.id)
        browser = _spell(action)
        if (
            browser.get("id") == "hold-monster"
            and browser.get("dc") == action.dc
            and browser.get("failedSaveTimedEffect", {}).get("effectId") == "paralyzed"
            and browser.get("excludedTargetCreatureTypes") == ["undead"]
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Hold Monster semantics"})
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
