#!/usr/bin/env python3
"""Audit direct Recharge save-for-half typed-damage Actions across all 2014 cards."""
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

from app.content.capability_compiler import _compile_save
from app.content.monster_save_capabilities_2014 import (
    save_capabilities_2014,
    supports_recharge_rules_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from browser_template_serializer import _save

OUTPUT = ROOT / "docs/generated/RECHARGE_SAVE_HALF_DAMAGE_BINDINGS_2014.json"
_HEADING = re.compile(r".+ \(Recharge [1-6](?:[-–][1-6])?\)$", re.I)
_DIRECT = re.compile(
    r".+?\. Each creature .+? must make a DC (?P<dc>\d+) "
    r"(?P<ability>\w+) saving throw, taking \d+ "
    r"\((?P<count>\d+)d(?P<size>\d+)(?: \+ (?P<bonus>\d+))?\) "
    r"(?P<damage_type>\w+) damage on a failed save, or half as much damage "
    r"on a successful one\.(?: Being underwater doesn't grant resistance "
    r"against this damage\.)?",
    re.I,
)


def _resource_id(monster, heading: str) -> str | None:
    label = heading.split(" (Recharge", 1)[0].strip().casefold()
    matches = [
        item for item in monster.action_recharges
        if item.replace("-", " ").casefold() == label
    ]
    return matches[0] if len(matches) == 1 else None


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for monster in monsters:
        for heading, printed in source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).items():
            text = " ".join(printed.split())
            match = _DIRECT.fullmatch(text)
            if _HEADING.fullmatch(heading) is None or match is None:
                continue
            resource_id = _resource_id(monster, heading)
            capabilities = save_capabilities_2014(monster)
            matches = [item for item in capabilities if item.id == resource_id]
            python_wired = len(matches) == 1 and supports_recharge_rules_2014(monster)
            browser_wired = False
            parameters: dict[str, object] | None = None
            if python_wired:
                card = matches[0]
                parameters = {
                    "save_ability": card.save_ability,
                    "dc": card.dc,
                    "range_ft": card.range_ft,
                    "area": card.area.model_dump(exclude_none=True) if card.area else None,
                    "damage_dice": f"{card.damage.count}d{card.damage.size}"
                    + (f"+{card.damage.bonus}" if card.damage and card.damage.bonus else ""),
                    "damage_type": card.damage_type,
                    "success_damage": card.success_damage,
                    "recharge_minimum": monster.action_recharges.get(resource_id),
                }
                expected = {
                    "dc": int(match["dc"]),
                    "save_ability": match["ability"].casefold(),
                    "damage_type": match["damage_type"].casefold(),
                    "damage_dice": f"{match['count']}d{match['size']}"
                    + (f"+{match['bonus']}" if match["bonus"] else ""),
                }
                actual = {key: parameters[key] for key in expected}
                if actual != expected:
                    python_wired = False
                    exceptions.append({"card_id": monster.id, "reason": "source_parameter_mismatch"})
                else:
                    try:
                        browser = _save(_compile_save(card))
                        browser_wired = (
                            browser["dc"] == card.dc
                            and browser["saveAbility"] == card.save_ability
                            and browser["damageType"] == card.damage_type
                            and browser["successDamage"] == "half"
                            and browser["resourceId"] == resource_id
                        )
                    except Exception:
                        browser_wired = False
            if not python_wired and not any(item["card_id"] == monster.id for item in exceptions):
                exceptions.append({"card_id": monster.id, "reason": "missing_python_binding"})
            elif python_wired and not browser_wired:
                exceptions.append({"card_id": monster.id, "reason": "missing_browser_binding"})
            rows.append({
                "card_id": monster.id,
                "card_name": monster.name,
                "source_action": heading,
                "source_text": text,
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
