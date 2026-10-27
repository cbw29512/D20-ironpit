"""Scan all 327 cards for source-declared innate Blindness/Deafness behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_BLINDNESS_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spell_save_dc_2014, innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _spell


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "blindness-deafness"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Blindness/Deafness rows"})
            continue
        row = declared[0]
        actions = [
            action for action in innate_spell_save_actions_2014(card)
            if action.id == "blindness-deafness"
        ]
        resources = {item.id: item for item in innate_spell_resources_2014(card)}
        if len(actions) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action = actions[0]
        effect = action.failed_save_timed_effect
        resource = resources.get("blindness-deafness")
        expected_dc = innate_spell_save_dc_2014(card)
        if (
            str(row.get("usage") or "") != "per_day"
            or int(row.get("uses_per_day") or 0) != 1
            or expected_dc is None or action.dc != expected_dc
            or resource is None or resource.max_uses != 1
            or action.level != 2 or action.action_cost != "action" or action.range_ft != 30
            or not action.requires_target_sight or action.save_ability != "constitution"
            or action.concentration or action.duration_minutes != 1 or effect is None
            or effect.effect_id != "blinded" or effect.duration_rounds != 10
            or effect.expiry_timing != "target_turn_end"
            or effect.repeat_save_ability != "constitution"
            or effect.repeat_save_dc != expected_dc
            or effect.repeat_save_timing != "target_turn_end"
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action/resource lost source parameters"})
            continue
        python_wired.append(card.id)
        browser = _spell(action)
        browser_effect = browser.get("failedSaveTimedEffect") or {}
        if (
            browser.get("id") == "blindness-deafness"
            and browser.get("range") == 30 and browser.get("requiresTargetSight") is True
            and browser.get("saveAbility") == "constitution" and browser.get("dc") == expected_dc
            and browser.get("concentration") is False
            and browser_effect.get("effectId") == "blinded"
            and browser_effect.get("durationRounds") == 10
            and browser_effect.get("repeatSaveAbility") == "constitution"
            and browser_effect.get("repeatSaveDc") == expected_dc
            and browser_effect.get("repeatSaveTiming") == "target_turn_end"
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Blindness semantics"})
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
