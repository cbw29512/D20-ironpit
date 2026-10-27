"""Scan all 327 cards for source-declared innate Blur behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_BLUR_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _timed_self_buff


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "blur"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Blur source rows"})
            continue
        row = declared[0]
        actions = [action for action in innate_timed_self_buffs_2014(card) if action.id == "blur"]
        resources = {item.id: item for item in innate_spell_resources_2014(card)}
        if len(actions) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action = actions[0]
        effect = action.modifier_effects[0] if len(action.modifier_effects) == 1 else None
        resource = resources.get("blur")
        if (
            str(row.get("usage") or "") != "per_day"
            or int(row.get("uses_per_day") or 0) != 1
            or resource is None or resource.max_uses != 1
            or action.action_cost != "action" or action.resource_id != "blur"
            or action.resource_cost != 1 or action.duration_rounds != 10
            or action.expiry_timing != "source_turn_start"
            or not action.magical_effect or not action.concentration
            or effect is None or effect.kind != "attacks-against-disadvantage"
            or effect.bypass_attacker_senses != ["blindsight", "truesight"]
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action/resource lost source parameters"})
            continue
        python_wired.append(card.id)
        browser = _timed_self_buff(action)
        browser_effects = browser.get("modifierEffects") or []
        if (
            browser.get("id") == "blur" and browser.get("actionCost") == "action"
            and browser.get("resourceId") == "blur" and browser.get("resourceCost") == 1
            and browser.get("durationRounds") == 10 and browser.get("concentration") is True
            and browser.get("magicalEffect") is True and len(browser_effects) == 1
            and browser_effects[0].get("kind") == "attacks-against-disadvantage"
            and browser_effects[0].get("bypassAttackerSenses") == ["blindsight", "truesight"]
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost innate Blur semantics"})
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
