"""Scan all immutable 2014 cards for on-hit target-turn-end recurring damage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "END_TURN_RECURRING_DAMAGE_BINDINGS_2014.json"

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

_PATTERN = re.compile(
    r"if the target is a creature(?: or a flammable object)?, it ignites\. "
    r"until a creature takes an action to douse the fire, the target takes "
    r"\d+ \((\d+)d(\d+)\) ([a-z]+) damage at the end of each of its turns\.",
    re.IGNORECASE,
)


def report() -> dict:
    cards = load_monster_source_2014()
    applicable: list[str] = []
    parameters: list[dict] = []
    exceptions: list[dict] = []
    for card in cards:
        for action_name, text in source_sections_2014(card.source_actions).items():
            match = _PATTERN.search(text)
            if match is None:
                continue
            applicable.append(card.id)
            dice_count, dice_size, damage_type = match.groups()
            parameters.append({
                "monster": card.id, "action": action_name,
                "apply_on": "hit", "dice_count": int(dice_count),
                "dice_size": int(dice_size), "damage_type": damage_type.casefold(),
                "tick_timing": "target_turn_end", "removal_action_cost": "action",
            })
            exceptions.append({
                "monster": card.id,
                "reason": (
                    "source permits a creature to douse the fire but omits the grid range "
                    "for a different creature performing that Action"
                ),
                "missing_fields": ["removal_action_range_ft"],
            })
    applicable = sorted(set(applicable))
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "source_declared_parameters": parameters,
        "wired_python_card_count": 0,
        "wired_browser_card_count": 0,
        "wired_cards": [],
        "remaining_card_count": len(applicable),
        "exceptions": exceptions,
        "status": "blocked: source omits another-creature douse Action range",
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
