"""Scan all 327 cards for failed-save conditions with start-turn damage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = (
    ROOT / "docs" / "generated" / "START_TURN_DAMAGE_CONDITION_BINDINGS_2014.json"
)

from app.content.monster_save_condition_validation_2014 import (
    supported_save_condition_2014,
)
from app.content.monster_semantic_start_turn_damage_2014 import (
    semantic_start_turn_damage_names_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_start_turn_damage_condition_2014 import (
    source_completed_start_turn_damage_condition_2014,
)


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, wired, exceptions = [], [], []
    for card in cards:
        names = semantic_start_turn_damage_names_2014(card)
        if not names:
            continue
        applicable.append(card.id)
        attacks = {attack.name: attack for attack in card.attacks}
        card_wired = True
        for name in names:
            attack = attacks.get(name)
            if attack is None:
                card_wired = False
                exceptions.append({
                    "monster": card.id,
                    "ability": name,
                    "reason": "semantic source action has no structured attack row",
                })
                continue
            completed = source_completed_start_turn_damage_condition_2014(
                card, attack
            )
            if (
                not completed.source_complete
                or not supported_save_condition_2014(
                    completed.on_hit_save_effect
                )
            ):
                card_wired = False
                exceptions.append({
                    "monster": card.id,
                    "ability": name,
                    "reason": (
                        "printed parameters do not exactly match "
                        "start-turn damage-condition schema"
                    ),
                })
        if card_wired:
            wired.append(card.id)
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "wired_cards": wired,
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": (
            "complete" if not exceptions
            else "partial: explicit exceptions remain"
        ),
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
        if (
            not args.output.exists()
            or args.output.read_text(encoding="utf-8") != rendered
        ):
            raise SystemExit(
                f"{args.output} is stale; regenerate with this script."
            )
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
