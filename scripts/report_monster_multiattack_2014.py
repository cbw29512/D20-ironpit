"""Single-pass 327-monster Multiattack coverage, reusing existing compiler.

Usage: python scripts/report_monster_multiattack_2014.py
"""
from __future__ import annotations

import json
from collections import Counter

from app.content.monster_multiattack_2014 import multiattack_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014


def report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    counts: Counter[str] = Counter()
    missing: list[dict[str, object]] = []
    for card in monsters:
        # Source cards without Multiattack have no sequence to bind.
        printed = source_sections_2014(card.source_actions).get("Multiattack")
        declared = bool(
            card.multiattack_slots or card.multiattack_binding is not None
            or card.multiattack_policy is not None
        )
        if printed is None and not declared:
            counts["not_applicable"] += 1
            continue
        reasons = (
            ["multiattack:source-unbound"] if printed and not declared
            else ["multiattack:missing-source"] if not printed
            else multiattack_blockers_2014(card)
        )
        if reasons:
            counts["blocked"] += 1
            missing.append({
                "monster": card.id,
                "reasons": reasons,
                "printed_multiattack": printed,
                "source_slots": card.multiattack_slots,
                "source_policy": card.multiattack_policy,
                "source_binding": card.multiattack_binding,
            })
        else:
            counts["bound"] += 1
    if len(monsters) != 327:
        raise ValueError("Expected 327 distinct 2014 monster cards")
    return {"source_monsters": 327, "counts": dict(sorted(counts.items())),
            "unresolved": missing}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
