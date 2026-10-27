"""Scan all 327 cards for source-declared innate Nondetection behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_NONDETECTION_BINDINGS_2014.json"

from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_innate_source_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    innate_spells_2014,
)
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "nondetection"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Nondetection rows"})
            continue
        row = declared[0]
        if (
            row.get("usage") != "at_will"
            or row.get("uses_per_day") is not None
            or row.get("shared_pool") is not False
            or str(row.get("qualifier") or "").casefold() != "self only"
            or "nondetection" not in ARENA_NEUTRAL_INNATE_SPELLS_2014
            or not supports_innate_spellcasting_2014(card)
        ):
            exceptions.append({"monster": card.id, "reason": "source parameters are incomplete or not explicitly arena-neutral"})
            continue
        definition = adapt_basic_monster_2014(card)
        action_ids = {
            *(action.id for action in definition.timed_self_buff_actions),
            *(action.id for action in definition.spell_save_actions),
        }
        resource_ids = {resource.id for resource in definition.resources}
        if "nondetection" in action_ids or "nondetection" in resource_ids:
            exceptions.append({"monster": card.id, "reason": "Python invented a combat action or resource"})
            continue
        python_wired.append(card.id)
        browser = template_row(compile_combatant(definition))
        browser_action_ids = {
            *(action.get("id") for action in browser.get("timed_self_buff_actions", [])),
            *(action.get("id") for action in browser.get("spell_save_actions", [])),
        }
        if "nondetection" not in browser_action_ids and "nondetection" not in (browser.get("resources") or {}):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser invented a combat action or resource"})
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
