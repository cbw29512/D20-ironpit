#!/usr/bin/env python3
"""Audit surprise-opening damage and Advantage across all 2014 source cards."""
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
from app.content.monster_opening_initiative_2014 import (
    opening_initiative_advantage_source_2014,
    opening_initiative_damage_source_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from browser_template_serializer import template_row

OUTPUT = ROOT / "docs/generated/SURPRISE_OPENING_BINDINGS_2014.json"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for monster in monsters:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        surprise_sections = {
            heading: text for heading, text in sections.items()
            if "surprises a creature" in text.casefold()
            and "first round of combat" in text.casefold()
        }
        advantage_sections = {
            heading: text for heading, text in sections.items()
            if "advantage on attack rolls" in text.casefold()
            and "creature it has surprised" in text.casefold()
        }
        if not surprise_sections and not advantage_sections:
            continue
        python_wired = browser_wired = False
        failure_reason: str | None = None
        parameters: dict[str, object] = {}
        try:
            damage_name = opening_initiative_damage_source_2014(monster)
            advantage_name = opening_initiative_advantage_source_2014(monster)
            python_wired = (
                bool(damage_name) == bool(surprise_sections)
                and bool(advantage_name) == bool(advantage_sections)
            )
            template = compile_combatant(adapt_monster_mechanics_2014(monster))
            attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
            browser_attacks = template_row(template)["attacks"]
            python_wired = python_wired and all(
                any(item.trigger == "round1_initiative_lead" for item in attack.conditional_damage)
                == bool(surprise_sections)
                for attack in attacks
            ) and all(
                any(item.trigger == "round1_initiative_lead" for item in attack.conditional_attack_advantage)
                == bool(advantage_sections)
                for attack in attacks
            )
            browser_wired = python_wired and all(
                (row.get("conditionalDamage", {}).get("trigger") == "round1_initiative_lead")
                == bool(surprise_sections)
                and (
                    any(item.get("trigger") == "round1_initiative_lead"
                        for item in row.get("conditionalAttackAdvantage", []))
                    == bool(advantage_sections)
                )
                for row in browser_attacks
            )
            parameters = {
                "surprise_damage_trait": damage_name,
                "surprise_damage_text": surprise_sections.get(damage_name),
                "ambusher_trait": advantage_name,
                "ambusher_text": advantage_sections.get(advantage_name),
                "attacks": [
                    {
                        "attack_id": attack.id,
                        "damage_dice": next((
                            f"{item.dice_count}d{item.dice_size}"
                            for item in attack.conditional_damage
                            if item.trigger == "round1_initiative_lead"
                        ), None),
                        "damage_type": next((
                            item.damage_type.value for item in attack.conditional_damage
                            if item.trigger == "round1_initiative_lead"
                        ), None),
                        "advantage": bool(attack.conditional_attack_advantage),
                    }
                    for attack in attacks
                ],
            }
        except Exception as exc:
            python_wired = browser_wired = False
            failure_reason = str(exc)
        if not python_wired:
            reason = "missing_or_mismatched_python_binding"
            if failure_reason:
                reason = f"{reason}: {failure_reason}"
            exceptions.append({"card_id": monster.id, "reason": reason})
        elif not browser_wired:
            exceptions.append({"card_id": monster.id, "reason": "missing_or_mismatched_browser_binding"})
        rows.append({
            "card_id": monster.id,
            "card_name": monster.name,
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
    rendered = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text() == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
