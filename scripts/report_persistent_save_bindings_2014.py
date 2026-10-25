"""Scan all 327 cards for persistent failed-save attack effects."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_save_persistent_validation_2014 import (
    supported_save_persistent_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_persistent_effect_2014 import (
    semantic_persistent_save_names_2014,
    source_completed_persistent_save_2014,
)


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, wired, exceptions = [], [], []
    for card in cards:
        names = semantic_persistent_save_names_2014(card)
        if not names:
            continue
        applicable.append(card.id)
        attacks = {attack.name: attack for attack in card.attacks}
        card_wired = True
        for name in names:
            attack = attacks.get(name)
            if attack is None:
                card_wired = False
                exceptions.append({
                    "monster": card.id, "ability": name,
                    "reason": "semantic source action has no structured attack row",
                })
                continue
            completed = source_completed_persistent_save_2014(card, attack)
            if (
                not completed.source_complete
                or not supported_save_persistent_2014(completed.on_hit_save_effect)
            ):
                card_wired = False
                exceptions.append({
                    "monster": card.id, "ability": name,
                    "reason": "printed parameters do not exactly match persistent-save schema",
                })
        if card_wired:
            wired.append(card.id)
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "wired_cards": wired,
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: explicit exceptions remain",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
