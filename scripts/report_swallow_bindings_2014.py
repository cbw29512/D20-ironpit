#!/usr/bin/env python3
"""Audit semantic Swallow/Engulf cards across the immutable 2014 corpus."""
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

from app.content.demo import build_demo_fighter
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.swallow_actions import swallow_action_from_source
from browser_template_serializer import template_row
OUTPUT = ROOT / "docs/generated/SWALLOW_BINDINGS_2014.json"
_SEMANTIC = re.compile(r"\b(?:swallow(?:s|ed)?|engulf(?:s|ed)?)\b", re.I)


def _source_text(monster) -> str:
    sections = source_sections_2014(monster.source_actions, include_continuations=True)
    selected = [text for heading, text in sections.items()
                if _SEMANTIC.search(heading) or _SEMANTIC.search(text)]
    return " ".join(" ".join(text.split()) for text in selected)


def _incompatibility(monster) -> str:
    if not monster.swallow_actions:
        return "missing_structured_source_parameters"
    data = monster.swallow_actions[0]
    if data.get("attack_id") is None or data.get("start_turn_save_dc") is not None:
        return "engulf_start_turn_save_profile_not_supported"
    if data.get("requires_existing_grapple") is False:
        return "failed_save_on_bite_profile_not_supported"
    if data.get("regurgitation_damage_threshold") is not None:
        return "damage_threshold_regurgitation_profile_not_supported"
    return "source_profile_not_supported"


def build_report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for monster in monsters:
        printed = _source_text(monster)
        if not monster.swallow_actions and not (
            _SEMANTIC.search(printed) and "blinded" in printed.casefold()
            and "restrained" in printed.casefold()
        ):
            continue
        profile = source_grapple_swallow_2014(monster)
        python_wired = profile is not None
        browser_wired = False
        parameters = None
        if profile is not None:
            parameters = {
                "attack_id": profile.attack_id,
                "delivery_mode": profile.delivery_mode,
                "max_target_size": profile.max_target_size.value,
                "damage_dice": f"{profile.damage_dice_count}d{profile.damage_dice_size}",
                "damage_type": profile.damage_type,
                "max_swallowed": profile.max_swallowed,
                "exit_movement_ft": profile.exit_movement_ft,
                "requires_existing_grapple": True,
            }
            if profile.regurgitation_damage_threshold is not None:
                parameters.update({
                    "regurgitation_damage_threshold": profile.regurgitation_damage_threshold,
                    "regurgitation_save_ability": profile.regurgitation_save_ability,
                    "regurgitation_save_dc": profile.regurgitation_save_dc,
                    "regurgitation_range_ft": profile.regurgitation_range_ft,
                    "regurgitation_all_swallowed": profile.regurgitation_all_swallowed,
                })
            action = swallow_action_from_source(profile).model_copy(update={
                "attack_id": f"2014-{monster.id}-{profile.attack_id}",
            })
            serialized = template_row(
                build_demo_fighter().model_copy(update={"swallow_actions": [action]})
            ).get("swallowActions", [])
            expected = {
                "sourceName": profile.source_name,
                "attackId": f"2014-{monster.id}-{profile.attack_id}",
                "requiresExistingGrapple": True,
                "maxTargetSize": profile.max_target_size.value,
                "damageDiceCount": profile.damage_dice_count,
                "damageDiceSize": profile.damage_dice_size,
                "damageType": profile.damage_type,
                "maxSwallowed": profile.max_swallowed,
                "exitMovementFt": profile.exit_movement_ft,
                "grantsTotalExternalCover": True,
                "blindsAndRestrains": True,
            }
            if profile.delivery_mode != "action_attack":
                expected["deliveryMode"] = profile.delivery_mode
            if profile.regurgitation_damage_threshold is not None:
                expected.update({
                    "regurgitationDamageThreshold": profile.regurgitation_damage_threshold,
                    "regurgitationSaveAbility": profile.regurgitation_save_ability,
                    "regurgitationSaveDc": profile.regurgitation_save_dc,
                    "regurgitationRangeFt": profile.regurgitation_range_ft,
                    "regurgitationAllSwallowed": profile.regurgitation_all_swallowed,
                })
            browser_wired = len(serialized) == 1 and serialized[0] == expected
        if not (python_wired and browser_wired):
            exceptions.append({"card_id": monster.id, "reason": _incompatibility(monster)})
        rows.append({
            "card_id": monster.id,
            "card_name": monster.name,
            "source_text": printed,
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
        "status": "partial" if len(wired) != len(rows) else "complete",
    }


def render() -> str:
    return json.dumps(build_report(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
