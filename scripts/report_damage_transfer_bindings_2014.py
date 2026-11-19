#!/usr/bin/env python3
"""Audit source-semantic Damage Transfer across all immutable 2014 cards."""
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
from app.content.monster_damage_transfer_2014 import damage_transfer_rule_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from browser_template_serializer import template_row

OUTPUT = ROOT / "docs/generated/DAMAGE_TRANSFER_BINDINGS_2014.json"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for monster in monsters:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        matches = {
            heading: " ".join(text.split()) for heading, text in sections.items()
            if "takes only half the damage dealt to it" in text.casefold()
            or "takes the other half" in text.casefold()
        }
        if not matches:
            continue
        python_wired = browser_wired = False
        reason: str | None = None
        parameters: dict[str, object] = {}
        try:
            rule = damage_transfer_rule_2014(monster)
            template = compile_combatant(adapt_monster_mechanics_2014(monster))
            browser = template_row(template).get("damage_transfer")
            python_wired = rule is not None and template.damage_transfer == rule
            browser_wired = python_wired and browser == rule.model_dump(mode="json")
            parameters = {
                **rule.model_dump(mode="json"),
                "source_text": matches.get(rule.source_name),
            }
        except Exception as exc:
            reason = str(exc)
        if not python_wired:
            exceptions.append({
                "card_id": monster.id,
                "reason": f"missing_or_mismatched_python_binding: {reason or 'unknown'}",
            })
        elif not browser_wired:
            exceptions.append({
                "card_id": monster.id, "reason": "missing_or_mismatched_browser_binding",
            })
        rows.append({
            "card_id": monster.id, "card_name": monster.name,
            "parameters": parameters, "python_wired": python_wired,
            "browser_wired": browser_wired,
        })
    wired = [row["card_id"] for row in rows if row["python_wired"] and row["browser_wired"]]
    return {
        "source_cards_scanned": len(monsters),
        "applicable_card_count": len(rows),
        "wired_python_card_count": sum(bool(row["python_wired"]) for row in rows),
        "wired_browser_card_count": sum(bool(row["browser_wired"]) for row in rows),
        "remaining_card_count": len(rows) - len(wired),
        "applicable_cards": [row["card_id"] for row in rows],
        "wired_cards": wired, "exceptions": exceptions, "bindings": rows,
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
