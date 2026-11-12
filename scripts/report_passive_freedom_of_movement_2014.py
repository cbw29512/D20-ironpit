#!/usr/bin/env python3
"""Audit passive Freedom of Movement bindings across all 327 source cards."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_freedom_of_movement_2014 import (
    passive_freedom_of_movement_grants_2014,
)
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_trait_bindings_2014 import progression_features_2014
from browser_template_serializer import template_row

OUTPUT = ROOT / "docs/generated/PASSIVE_FREEDOM_OF_MOVEMENT_BINDINGS_2014.json"
REQUIRED_PHRASES = (
    "ignores difficult terrain",
    "magical effects can't reduce its speed",
    "spend 5 feet of movement",
    "nonmagical restraints or being grappled",
)


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    commoner = next(item for item in monsters if item.id == "commoner")
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for monster in monsters:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        matches = {
            heading: text for heading, text in sections.items()
            if all(phrase in text.casefold().replace("’", "'") for phrase in REQUIRED_PHRASES)
        }
        if not matches:
            continue
        grants = passive_freedom_of_movement_grants_2014(monster)
        probe = adapt_monster_mechanics_2014(commoner).model_copy(update={
            "id": "2014-source-neutral-passive-probe",
            "name": "Source-neutral Passive Probe",
            "progression_features": progression_features_2014(monster),
        })
        template = compile_combatant(probe)
        browser = template_row(template).get("passive_debuff_counter_grants", [])
        python_wired = len(matches) == 1 and len(grants) == 5
        browser_wired = python_wired and browser == [
            grant.model_dump(mode="json") for grant in grants
        ]
        if not python_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_or_ambiguous_python_binding"})
        elif not browser_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_browser_binding"})
        rows.append({
            "card_id": monster.id,
            "card_name": monster.name,
            "source_sections": matches,
            "parameters": [grant.counter.model_dump(mode="json") for grant in grants],
            "python_wired": python_wired,
            "browser_wired": browser_wired,
        })
    wired = [row["card_id"] for row in rows if row["python_wired"] and row["browser_wired"]]
    source_2024 = json.loads(
        (ROOT / "frontend/data/srd_5_2_1_monsters.json").read_text()
    )
    paired_2024 = [
        item["id"] for item in source_2024
        if all(
            phrase in str(item.get("traits", "")).casefold().replace("’", "'")
            for phrase in REQUIRED_PHRASES
        )
    ]
    return {
        "source_cards_scanned": len(monsters),
        "applicable_card_count": len(rows),
        "wired_python_card_count": sum(bool(row["python_wired"]) for row in rows),
        "wired_browser_card_count": sum(bool(row["browser_wired"]) for row in rows),
        "remaining_card_count": len(rows) - len(wired),
        "applicable_cards": [row["card_id"] for row in rows],
        "wired_cards": wired,
        "exceptions": exceptions,
        "bindings": rows,
        "paired_2024_reuse": {
            "source_cards_scanned": len(source_2024),
            "applicable_card_count": len(paired_2024),
            "applicable_cards": paired_2024,
            "note": "No 2014 parameters are copied when the pinned 2024 source omits the declaration.",
        },
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
