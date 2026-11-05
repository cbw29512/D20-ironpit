#!/usr/bin/env python3
"""Audit all 327 cards for source-semantic thought-reading Actions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_read_thoughts_neutral_2014 import (
    semantic_read_thoughts_action_labels_2014,
    source_proven_noncombat_read_thoughts_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

OUTPUT = ROOT / "docs/generated/READ_THOUGHTS_CLASSIFICATION_2014.json"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    for monster in monsters:
        sections = source_sections_2014(monster.source_actions)
        for label in semantic_read_thoughts_action_labels_2014(monster):
            wired = source_proven_noncombat_read_thoughts_2014(monster, label)
            rows.append({
                "card_id": monster.id,
                "card_name": monster.name,
                "action_label": label,
                "source_text": sections[label],
                "classification_wired": wired,
            })
    wired = [row for row in rows if row["classification_wired"]]
    exceptions = [
        {"card_id": row["card_id"], "reason": "unsupported_source_clause"}
        for row in rows if not row["classification_wired"]
    ]
    return {
        "source_cards_scanned": len(monsters),
        "applicable_card_count": len(rows),
        "wired_card_count": len(wired),
        "remaining_card_count": len(rows) - len(wired),
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
