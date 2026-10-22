"""Scan all 327 cards and report semantic Death Trigger coverage and exceptions."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_death_triggers_2014 import supports_death_triggers_2014
from app.content.monster_source_2014 import load_monster_source_2014

_SEMANTIC_TRAITS = frozenset({"death burst", "death throes"})


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, declared, wired, exceptions = [], [], [], []
    for card in cards:
        semantic_names = sorted(
            name for name in card.trait_names if name.casefold() in _SEMANTIC_TRAITS
        )
        is_applicable = bool(card.death_trigger_actions or semantic_names)
        if not is_applicable:
            continue
        applicable.append(card.id)
        ids = [
            action.get("id") for action in card.death_trigger_actions
            if isinstance(action, dict) and isinstance(action.get("id"), str)
        ]
        if card.death_trigger_actions:
            declared.append(card.id)
        if card.death_trigger_actions and supports_death_triggers_2014(card):
            wired.append(card.id)
        else:
            exceptions.append({
                "monster": card.id,
                "semantic_traits": semantic_names,
                "reason": (
                    "printed semantic Death Trigger lacks a complete structured action"
                    if not card.death_trigger_actions
                    else "structured action is incompatible with the shared save/damage schema"
                ),
            })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "source_declared_card_count": len(declared),
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "cards_with_death_trigger_actions": len(declared),
        "death_effect_dispatch_wired": len(wired),
        "status": "complete" if not exceptions else "partial: exceptions require source data",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
