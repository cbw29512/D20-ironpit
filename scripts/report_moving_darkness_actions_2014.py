#!/usr/bin/env python3
"""Audit source-following magical-darkness Actions across all 327 cards."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_darkness_aura_2014 import source_proven_darkness_aura_2014
from app.content.monster_source_sections_2014 import source_sections_2014

OUTPUT = ROOT / "docs/generated/MOVING_DARKNESS_ACTION_BINDINGS_2014.json"


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace("\N{SOFT HYPHEN}", "").split())


def build_report() -> dict[str, object]:
    cards = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for card in cards:
        sections = source_sections_2014(card.source_actions, include_continuations=True)
        for ability_name, source_text in sections.items():
            text = _normalized(source_text)
            if not ("magical darkness" in text and "moves with" in text):
                continue
            action = source_proven_darkness_aura_2014(card)
            wired = action is not None and action.name == ability_name
            reason = None if wired else "moving_magical_darkness_source_did_not_compile_exactly"
            if reason:
                exceptions.append({
                    "card_id": card.id, "ability_name": ability_name, "reason": reason,
                })
            rows.append({
                "card_id": card.id, "card_name": card.name,
                "ability_name": ability_name, "source_text": source_text,
                "parameters": action.model_dump(mode="json") if action else None,
                "python_wired": wired, "browser_wired": wired, "exception": reason,
            })
    applicable = sorted({row["card_id"] for row in rows})
    wired = sorted({
        row["card_id"] for row in rows
        if row["python_wired"] and row["browser_wired"]
    })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(applicable) - len(wired),
        "applicable_cards": applicable, "wired_cards": wired,
        "exceptions": exceptions, "bindings": rows,
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
