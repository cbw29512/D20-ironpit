"""Report death-trigger source-card binding coverage without claiming runtime execution.

Run: python scripts/report_death_trigger_bindings_2014.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_source_2014 import load_monster_source_2014


def report() -> dict:
    cards = load_monster_source_2014()
    declared = []
    invalid = []
    for card in cards:
        if not card.death_trigger_actions:
            continue
        ids = []
        for action in card.death_trigger_actions:
            if not isinstance(action, dict) or not isinstance(action.get("id"), str) or not action["id"]:
                invalid.append(card.id)
                continue
            ids.append(action["id"])
        declared.append({"monster": card.id, "effect_ids": ids, "actions": card.death_trigger_actions})
    return {
        "source_cards": len(cards),
        "cards_with_death_trigger_actions": len(declared),
        "cards_with_valid_death_trigger_identifiers": len(declared) - len(set(invalid)),
        "cards_with_invalid_death_trigger_actions": sorted(set(invalid)),
        "source_declarations": declared,
        "death_effect_dispatch_wired": 0,
        "status": "partial: source declaration and buff initialization; effect dispatch pending",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
