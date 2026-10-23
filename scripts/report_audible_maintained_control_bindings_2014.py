"""Scan all 327 cards for audible maintained control coverage and exceptions."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_audible_maintained_control_2014 import (
    semantic_audible_control_candidate_names_2014,
    source_proven_audible_maintained_controls_2014,
    supports_audible_maintained_controls_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, wired, exceptions = [], [], []
    for card in cards:
        names = list(semantic_audible_control_candidate_names_2014(card))
        if not names:
            continue
        applicable.append(card.id)
        actions = source_proven_audible_maintained_controls_2014(card)
        if actions and supports_audible_maintained_controls_2014(card):
            wired.append(card.id)
        else:
            exceptions.append({
                "monster": card.id,
                "semantic_actions": names,
                "reason": (
                    "printed audible maintained control has incomplete or incompatible "
                    "targeting, upkeep, movement, repeat-save, duration, or immunity clauses"
                ),
            })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: exceptions require source/schema support",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
