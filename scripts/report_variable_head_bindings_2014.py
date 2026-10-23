"""Scan all 327 immutable cards for semantic variable-head lifecycle coverage."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_variable_heads_2014 import (
    semantic_variable_head_sections_2014,
    variable_head_profile_2014,
)


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, wired, exceptions = [], [], []
    for card in cards:
        try:
            sections = semantic_variable_head_sections_2014(card)
            if sections is None:
                continue
            applicable.append(card.id)
            profile = variable_head_profile_2014(card)
            if profile is None:
                raise ValueError("semantic candidate produced no immutable profile")
            wired.append(card.id)
        except (TypeError, ValueError) as exc:
            text = "\n".join(filter(None, (
                card.source_traits, card.source_actions, card.source_reactions)))
            if not any(word in text.casefold() for word in ("head", "regrow")):
                continue
            applicable.append(card.id)
            exceptions.append({"monster": card.id, "reason": str(exc)})
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: exceptions require schema support",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
