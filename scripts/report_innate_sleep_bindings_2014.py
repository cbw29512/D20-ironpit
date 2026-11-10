"""Independently inspect 327 pinned 2014 cards for real typed Sleep spell binding."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "SLEEP_BINDINGS_2014.json"

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.shared_hp_pool_spells_2014 import sleep_2014
from scripts.browser_template_serializer import template_row


def _sleep_rows(card) -> list[tuple[str, dict]]:
    innate = [
        ("innate", row) for row in innate_spells_2014(card)
        if str(row.get("id") or "").casefold() == "sleep"
    ]
    prepared = card.spellcasting
    source = prepared if isinstance(prepared, dict) else (
        prepared.model_dump() if prepared else {}
    )
    innate.extend(
        ("prepared", row) for row in (source.get("spells") or [])
        if str(row.get("id") or "").casefold() == "sleep"
    )
    return innate


def _executable_binding(card) -> tuple[bool, bool, list[str]]:
    """Separate compiled Python evidence from browser serialization evidence."""
    errors = []
    try:
        action = sleep_2014()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        matches = [
            item for item in template.hit_point_pool_spell_actions
            if item.id == action.id
        ]
        python = matches == [action]
        if not python:
            errors.append("typed Python spell action missing or altered")
        if not python:
            return False, False, errors
        exported = template_row(template)
        browser_rows = [
            row for row in exported.get("hit_point_pool_spell_actions", [])
            if row.get("id") == action.id
        ]
        browser = len(browser_rows) == 1 and all(
            browser_rows[0].get(key) == value for key, value in {
                "name": action.name, "level": action.level,
                "range": action.range_ft, "areaRadius": action.area_radius_ft,
                "poolDiceCount": action.pool_dice_count,
                "poolDiceSize": action.pool_dice_size,
                "extraDicePerUpcastLevel": action.extra_dice_per_upcast_level,
                "conditionId": action.condition_id,
                "durationRounds": action.duration_rounds,
                "endsOnDamage": action.ends_on_damage,
                "allowedRemovalActionIds": action.allowed_removal_action_ids,
                "excludedCreatureTypes": action.excluded_creature_types,
                "excludedConditionImmunities": action.excluded_condition_immunities,
            }.items()
        )
        if not browser:
            errors.append("browser combatant spell serializer omits source effects")
        return python, browser, errors
    except Exception as exc:
        return False, False, [f"source/compile/serialize failed: {type(exc).__name__}: {exc}"]


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, declared_access, wired_python, wired_browser, exceptions = [], [], [], [], []
    for card in cards:
        rows = _sleep_rows(card)
        if not rows:
            continue
        applicable.append(card.id)
        if len(rows) != 1:
            exceptions.append({"monster": card.id, "reason": "card declares Sleep more than once"})
            continue
        kind, row = rows[0]
        declared_access.append({
            "monster": card.id, "source_kind": kind, "usage": row.get("usage"),
            "uses_per_day": row.get("uses_per_day"), "level": row.get("level"),
        })
        python, browser, issues = _executable_binding(card)
        if python:
            wired_python.append(card.id)
        if browser:
            wired_browser.append(card.id)
        for issue in issues:
            exceptions.append({"monster": card.id, "reason": issue})
    complete = sorted(set(wired_python) & set(wired_browser))
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "declared_access": declared_access,
        "wired_python_card_count": len(wired_python),
        "wired_browser_card_count": len(wired_browser),
        "wired_cards": complete,
        "remaining_card_count": len(applicable) - len(complete),
        "exceptions": exceptions,
        "shared_lifecycle_evidence": {
            "condition": "unconscious", "ends_on_damage_supported": True,
            "wake_action_id": "wake-sleeper",
            "python_browser_parity_test": "2014 Sleep HP-pool cast and Brass Dragon wake-up",
        },
        "status": "source-compiled and browser-serialized" if not exceptions else "blocked",
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
