"""Scan all 327 cards for source-declared innate Detect Magic behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_DETECT_MAGIC_BINDINGS_2014.json"

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    innate_spells_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row


def _runtime_ids(definition) -> tuple[set[str], set[str], set[str]]:
    action_ids = {
        *(action.id for action in definition.auto_hit_spell_actions),
        *(action.id for action in definition.spell_save_actions),
        *(action.id for action in definition.persistent_save_zone_actions),
        *(action.id for action in definition.timed_self_buff_actions),
    }
    resource_ids = {resource.id for resource in definition.resources}
    grant_ids = {
        grant.spell_id
        for grant in definition.progression_features.alternate_spell_cast_grants
    }
    return action_ids, resource_ids, grant_ids


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "detect-magic"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Detect Magic rows"})
            continue
        row = declared[0]
        usage = str(row.get("usage") or "")
        uses = row.get("uses_per_day")
        if (
            "detect-magic" not in ARENA_NEUTRAL_INNATE_SPELLS_2014
            or row.get("shared_pool") is not False
            or row.get("qualifier") is not None
            or (usage == "at_will" and uses is not None)
            or (usage == "per_day" and (not isinstance(uses, int) or uses <= 0))
            or usage not in {"at_will", "per_day"}
        ):
            exceptions.append({"monster": card.id, "reason": "source frequency is incomplete or spell is not explicitly arena-neutral"})
            continue
        definition = adapt_monster_mechanics_2014(card)
        if any("detect-magic" in ids for ids in _runtime_ids(definition)):
            exceptions.append({"monster": card.id, "reason": "Python invented a combat action, resource, or cast grant"})
            continue
        python_wired.append(card.id)
        browser = template_row(compile_combatant(definition))
        browser_action_ids = {
            *(action.get("id") for action in browser.get("auto_hit_spell_actions", [])),
            *(action.get("id") for action in browser.get("spell_save_actions", [])),
            *(action.get("id") for action in browser.get("persistent_save_zone_actions", [])),
            *(action.get("id") for action in browser.get("timed_self_buff_actions", [])),
        }
        browser_grants = {
            grant.get("spell_id")
            for grant in browser.get("alternate_spell_cast_grants", [])
        }
        if (
            "detect-magic" not in browser_action_ids
            and "detect-magic" not in (browser.get("resources") or {})
            and "detect-magic" not in browser_grants
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser invented a combat action, resource, or cast grant"})
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
