#!/usr/bin/env python3
"""Audit form-qualified Charge/Pounce bindings across all 327 source cards."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_form_qualified_charge_2014 import source_proven_form_qualified_charge_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from browser_template_serializer import attack_row

OUTPUT = ROOT / "docs/generated/FORM_QUALIFIED_CHARGE_BINDINGS_2014.json"
HEADING = re.compile(r"^(?:Charge|Pounce) \([^()]+ or Hybrid Form Only\)$", re.I)


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows = []
    exceptions = []
    for monster in monsters:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        headings = [name for name in sections if HEADING.fullmatch(name)]
        if not headings:
            continue
        proven = source_proven_form_qualified_charge_traits_2014(monster)
        template = compile_combatant(adapt_monster_mechanics_2014(monster))
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        charge_attacks = [attack for attack in attacks if attack.charge_profile is not None]
        python_wired = len(headings) == len(proven) == 1 and len(charge_attacks) == 1
        browser_wired = False
        parameters = None
        if python_wired:
            attack = charge_attacks[0]
            profile = attack.charge_profile
            browser = attack_row(attack, {"charge"}).get("charge")
            browser_wired = isinstance(browser, dict) and browser.get("minimumMove") == profile.minimum_move_ft
            parameters = {
                "trigger_attack_id": attack.id,
                "minimum_move_ft": profile.minimum_move_ft,
                "prone_save_ability": profile.prone_save_ability,
                "prone_save_dc": profile.prone_save_dc,
                "follow_up_attack_id": profile.follow_up_attack_id,
                "follow_up_action_cost": profile.follow_up_action_cost,
            }
        if not python_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_or_ambiguous_python_binding"})
        elif not browser_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_browser_binding"})
        rows.append({
            "card_id": monster.id,
            "card_name": monster.name,
            "source_trait": headings[0] if len(headings) == 1 else headings,
            "source_text": sections[headings[0]] if len(headings) == 1 else None,
            "parameters": parameters,
            "python_wired": python_wired,
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
        "wired_cards": wired,
        "exceptions": exceptions,
        "bindings": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_report(), indent=2, sort_keys=True, default=str) + "\n"
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text() == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
