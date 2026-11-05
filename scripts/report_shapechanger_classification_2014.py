#!/usr/bin/env python3
"""Audit all 2014 Shapechanger source clauses and arena classifications."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_shapechanger_neutral_2014 import source_proven_arena_inert_shapechanger_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

OUTPUT = ROOT / "docs/generated/SHAPECHANGER_CLASSIFICATION_2014.json"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows = []
    exceptions = []
    for monster in monsters:
        if "Shapechanger" not in monster.trait_names:
            continue
        source_text = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Shapechanger", "")
        wired = source_proven_arena_inert_shapechanger_2014(monster)
        reason = None if wired else "combat_active_form_requires_runtime_support"
        if reason:
            exceptions.append({"card_id": monster.id, "reason": reason})
        rows.append({
            "card_id": monster.id,
            "card_name": monster.name,
            "source_text": source_text,
            "classification_wired": wired,
            "runtime_required": not wired,
        })
    wired_cards = [row["card_id"] for row in rows if row["classification_wired"]]
    return {
        "source_cards_scanned": len(monsters),
        "applicable_card_count": len(rows),
        "wired_card_count": len(wired_cards),
        "remaining_card_count": len(rows) - len(wired_cards),
        "applicable_cards": [row["card_id"] for row in rows],
        "wired_cards": wired_cards,
        "exceptions": exceptions,
        "bindings": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text() == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
