#!/usr/bin/env python3
"""Audit source-semantic Smother actions across all immutable 2014 cards."""
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
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_smother_2014 import source_proven_smother_attacks_2014
from browser_template_serializer import template_row

OUTPUT = ROOT / "docs/generated/SMOTHER_BINDINGS_2014.json"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows, exceptions = [], []
    for monster in monsters:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        matches = {name: text for name, text in sections.items()
                   if "at risk of suffocating" in text.casefold()
                   and "can't smother another target" in text.casefold()}
        if not matches:
            continue
        definitions = source_proven_smother_attacks_2014(monster)
        python_wired = browser_wired = False
        parameters: dict[str, object] = {}
        reason = None
        try:
            definition, = definitions
            template = compile_combatant(adapt_monster_mechanics_2014(monster))
            attack = next(row for row in [template.weapon_attack, *template.alternate_weapon_attacks]
                          if row.id == definition.id)
            browser = next(row for row in template_row(template)["attacks"] if row["id"] == definition.id)
            control = attack.control_effect
            python_wired = bool(control and control.grapple_blinds and control.grapple_prevents_breathing)
            browser_wired = python_wired and browser.get("controlEffect", {}).get("grappleBlinds") is True
            parameters = {
                "attack_bonus": attack.attack_bonus, "reach_ft": attack.weapon.reach_ft,
                "escape_dc": control.grapple_escape_dc,
                "max_target_size": control.max_target_size.value,
                "periodic_damage": control.grapple_periodic_damage.model_dump(mode="json"),
                "source_text": matches[definition.name],
            }
        except Exception as exc:
            reason = str(exc)
        if not python_wired:
            exceptions.append({"card_id": monster.id, "reason": reason or "missing_python_binding"})
        elif not browser_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_browser_binding"})
        rows.append({"card_id": monster.id, "card_name": monster.name, "parameters": parameters,
                     "python_wired": python_wired, "browser_wired": browser_wired})
    wired = [row["card_id"] for row in rows if row["python_wired"] and row["browser_wired"]]
    return {
        "source_cards_scanned": len(monsters), "applicable_card_count": len(rows),
        "wired_python_card_count": sum(bool(row["python_wired"]) for row in rows),
        "wired_browser_card_count": sum(bool(row["browser_wired"]) for row in rows),
        "remaining_card_count": len(rows) - len(wired),
        "applicable_cards": [row["card_id"] for row in rows], "wired_cards": wired,
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
