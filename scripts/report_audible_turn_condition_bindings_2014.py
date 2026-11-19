#!/usr/bin/env python3
"""Audit audible one-turn conditions across all immutable 2014 source cards."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.capability_compiler import _compile_save
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_audible_turn_conditions_2014 import (
    source_proven_audible_turn_conditions_2014,
)
from browser_template_serializer import _save

OUTPUT = ROOT / "docs/generated/AUDIBLE_TURN_CONDITION_BINDINGS_2014.json"


def _candidate(text: str) -> bool:
    normalized = " ".join(text.casefold().split())
    return all(token in normalized for token in (
        "can hear", "saving throw", "until the end of", "next turn",
        "immune", "next 24 hours",
    ))


def build_report() -> dict[str, object]:
    cards = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for card in cards:
        sections = source_sections_2014(card.source_actions, include_continuations=True)
        candidates = {name: text for name, text in sections.items() if _candidate(text)}
        if not candidates:
            continue
        definitions = source_proven_audible_turn_conditions_2014(card)
        if len(definitions) != len(candidates):
            exceptions.append({
                "card_id": card.id,
                "reason": "source_candidate_did_not_compile_exactly",
            })
        for name, source_text in candidates.items():
            definition = next((item for item in definitions if item.name == name), None)
            python_wired = definition is not None
            browser_wired = False
            parameters: dict[str, object] = {"source_text": source_text}
            if definition is not None:
                browser = _save(_compile_save(definition))
                rider = browser.get("failedSaveTimedEffect", {})
                browser_wired = bool(
                    browser.get("requiresTargetHearing") is True
                    and browser.get("sourceEffectImmunityOnSuccess") is True
                    and rider.get("expiryTiming") == "source_turn_end"
                )
                parameters.update({
                    "save_ability": definition.save_ability,
                    "dc": definition.dc,
                    "radius_ft": definition.range_ft,
                    "excluded_target_creature_types": definition.excluded_target_creature_types,
                    "condition": definition.failed_save_timed_effect.effect_id,
                })
            if python_wired and not browser_wired:
                exceptions.append({"card_id": card.id, "reason": "missing_browser_binding"})
            rows.append({
                "card_id": card.id,
                "card_name": card.name,
                "ability_name": name,
                "parameters": parameters,
                "python_wired": python_wired,
                "browser_wired": browser_wired,
            })
    wired = [
        row["card_id"] for row in rows
        if row["python_wired"] and row["browser_wired"]
    ]
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(rows),
        "wired_python_card_count": sum(bool(row["python_wired"]) for row in rows),
        "wired_browser_card_count": sum(bool(row["browser_wired"]) for row in rows),
        "remaining_card_count": len(rows) - len(wired),
        "applicable_cards": [row["card_id"] for row in rows],
        "wired_cards": wired,
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
