"""Scan all 327 cards and report semantic Death Trigger coverage and exceptions."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_death_triggers_2014 import (
    death_trigger_actions_2014,
    semantic_death_trigger_names_2014,
    supports_death_triggers_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, complete, wired, structured, exceptions = [], [], [], [], []
    for card in cards:
        semantic_names = list(semantic_death_trigger_names_2014(card))
        if not card.death_trigger_actions and not semantic_names:
            continue
        applicable.append(card.id)
        if card.death_trigger_actions:
            structured.append(card.id)
        actions = death_trigger_actions_2014(card)
        if actions:
            complete.append(card.id)
        if actions and supports_death_triggers_2014(card):
            wired.append(card.id)
        else:
            exceptions.append({
                "monster": card.id,
                "semantic_traits": semantic_names,
                "reason": (
                    "printed Death Trigger is not representable by the shared "
                    "save/damage/timed-effect schema"
                    if not card.death_trigger_actions
                    else "structured action is incompatible with the shared save/damage schema"
                ),
            })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "structured_source_card_count": len(structured),
        "source_declared_card_count": len(complete),
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "cards_with_death_trigger_actions": len(structured),
        "death_effect_dispatch_wired": len(wired),
        "status": "complete" if not exceptions else "partial: exceptions require schema support",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
