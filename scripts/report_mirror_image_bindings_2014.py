"""Scan all 327 cards for source-declared 2014 Mirror Image behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "MIRROR_IMAGE_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014, innate_timed_self_buffs_2014
from app.content.monster_prepared_spells_2014 import _prepared_spells, prepared_timed_self_buffs_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014
from scripts.browser_template_serializer import _timed_self_buff


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, remaining = [], [], [], []
    for card in cards:
        prepared = [row for row in _prepared_spells(card) if row.get("id") == "mirror-image"]
        innate = [row for row in innate_spells_2014(card) if row.get("id") == "mirror-image"]
        if not prepared and not innate:
            continue
        applicable.append(card.id)
        if len(prepared) + len(innate) != 1:
            remaining.append({"monster": card.id, "reason": "multiple Mirror Image source rows"})
            continue
        row = (prepared or innate)[0]
        actions = [action for action in [
            *prepared_timed_self_buffs_2014(card), *innate_timed_self_buffs_2014(card),
        ] if action.id == "mirror-image"]
        expected_resource = "spell-slot-2" if prepared else "mirror-image"
        resources = {item.id: item for item in [
            *monster_spell_slot_resources_2014(card), *innate_spell_resources_2014(card),
        ]}
        if len(actions) != 1:
            remaining.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action = actions[0]
        rule = action.illusory_duplicate_defense
        expected_uses = resources[expected_resource].max_uses if expected_resource in resources else 0
        if (
            (prepared and row.get("level") != 2) or expected_uses <= 0
            or action.resource_id != expected_resource or action.resource_cost != 1
            or action.duration_rounds != 10 or action.concentration
            or rule is None or rule.initial_duplicates != 3
            or rule.redirect_minimum_by_duplicates != [0, 11, 8, 6]
            or rule.armor_class_base != 10 or rule.armor_class_ability != "dexterity"
            or rule.bypass_attacker_senses != ["blindsight", "truesight"]
        ):
            remaining.append({"monster": card.id, "reason": "compiled action/resource lost source parameters"})
            continue
        python_wired.append(card.id)
        browser = _timed_self_buff(action)
        browser_rule = browser.get("illusoryDuplicateDefense") or {}
        if (
            browser.get("resourceId") == expected_resource and browser.get("durationRounds") == 10
            and browser_rule.get("initialDuplicates") == 3
            and browser_rule.get("redirectMinimumByDuplicates") == [0, 11, 8, 6]
            and browser_rule.get("armorClassBase") == 10
            and browser_rule.get("armorClassAbility") == "dexterity"
            and browser_rule.get("bypassAttackerSenses") == ["blindsight", "truesight"]
        ):
            browser_wired.append(card.id)
        else:
            remaining.append({"monster": card.id, "reason": "browser serialization lost Mirror Image semantics"})
    cloaker = next(card for card in cards if card.id == "cloaker")
    exceptions = [{
        "monster": cloaker.id, "ability": "Phantasms",
        "disposition": "incompatible distinct mechanic; partial independent binding",
        "reason": (
            "uniform weapon-attack selection, source AC, and bright-light lifecycle are wired "
            "independently; harmful-spell save/attack targeting and duplicate saves remain"
        ),
    }] if "Phantasms" in cloaker.source_actions else []
    return {
        "source_cards_scanned": len(cards), "applicable_card_count": len(applicable),
        "applicable_cards": applicable, "wired_python_card_count": len(python_wired),
        "wired_browser_card_count": len(browser_wired),
        "wired_cards": sorted(set(python_wired) & set(browser_wired)),
        "remaining_card_count": len(remaining), "remaining": remaining,
        "exceptions": exceptions,
        "status": "complete" if not remaining else "partial: explicit remaining bindings",
    }


def render() -> str:
    return json.dumps(report(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is stale; regenerate with this script.")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
