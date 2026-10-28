"""Scan all 327 immutable cards for source-declared 2014 Sleep spell access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "SLEEP_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import load_monster_source_2014


_REQUIRED_SPELL_RULE_FIELDS = (
    "range_ft",
    "area_radius_ft",
    "pool_dice_count",
    "pool_dice_size",
    "duration_rounds",
    "ends_on_damage",
    "allowed_removal_action_ids",
    "excluded_creature_types",
    "excluded_condition_immunities",
)


def _prepared_spells(card) -> list[dict]:
    source = card.spellcasting
    if source is None:
        return []
    row = source if isinstance(source, dict) else source.model_dump()
    return list(row.get("spells") or [])


def _sleep_rows(card) -> list[tuple[str, dict]]:
    rows = [
        ("innate", row) for row in innate_spells_2014(card)
        if str(row.get("id") or "").casefold() == "sleep"
    ]
    rows.extend(
        ("prepared", row) for row in _prepared_spells(card)
        if str(row.get("id") or "").casefold() == "sleep"
    )
    return rows


def report() -> dict:
    cards = load_monster_source_2014()
    applicable: list[str] = []
    exceptions: list[dict] = []
    declared_access: list[dict] = []
    for card in cards:
        rows = _sleep_rows(card)
        if not rows:
            continue
        applicable.append(card.id)
        if len(rows) != 1:
            exceptions.append({
                "monster": card.id,
                "reason": "card declares Sleep more than once",
            })
            continue
        source_kind, row = rows[0]
        declared_access.append({
            "monster": card.id,
            "source_kind": source_kind,
            "usage": row.get("usage"),
            "uses_per_day": row.get("uses_per_day"),
            "level": row.get("level"),
        })
        missing = [field for field in _REQUIRED_SPELL_RULE_FIELDS if row.get(field) is None]
        if missing:
            exceptions.append({
                "monster": card.id,
                "reason": "monster card declares spell access but omits the Sleep effect payload",
                "missing_fields": missing,
            })
            continue
        exceptions.append({
            "monster": card.id,
            "reason": "complete Sleep payload is present but no shared Sleep action is wired",
        })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "declared_access": declared_access,
        "wired_python_card_count": 0,
        "wired_browser_card_count": 0,
        "wired_cards": [],
        "remaining_card_count": len(applicable),
        "exceptions": exceptions,
        "shared_lifecycle_evidence": {
            "condition": "unconscious",
            "ends_on_damage_supported": True,
            "wake_action_id": "wake-sleeper",
            "python_browser_parity_test": "2014 Brass Dragon Sleep Breath",
        },
        "status": "blocked: immutable monster cards omit required Sleep spell-rule parameters",
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
