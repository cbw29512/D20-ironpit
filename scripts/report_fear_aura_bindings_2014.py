"""Scan all 327 cards for passive hostile fear-aura behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "FEAR_AURA_BINDINGS_2014.json"

from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_semantic_fear_aura_2014 import (
    semantic_fear_aura_candidate_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _fear_actions(card) -> list:
    return [
        action
        for action in condition_auras_from_source(card.source_traits, "2014")
        if (
            action.activation_timing == "passive"
            and action.hostile_start_turn_condition_aura is not None
            and action.hostile_start_turn_condition_aura.trigger
            == "enemy_turn_start"
            and action.hostile_start_turn_condition_aura.condition_id
            == "frightened"
            and action.hostile_start_turn_condition_aura
            .requires_source_not_incapacitated
        )
    ]


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, wired, exceptions = [], [], []
    for card in cards:
        if not semantic_fear_aura_candidate_2014(card):
            continue
        applicable.append(card.id)
        actions = _fear_actions(card)
        if len(actions) != 1:
            exceptions.append({
                "monster": card.id,
                "reason": (
                    "printed fear-aura behavior did not compile to exactly "
                    "one passive hostile start-turn aura"
                ),
            })
            continue
        aura = actions[0].hostile_start_turn_condition_aura
        if (
            aura is None
            or aura.radius_ft <= 0
            or aura.save_dc <= 0
            or aura.condition_expiry_timing != "target_turn_start"
            or not aura.success_immunity
        ):
            exceptions.append({
                "monster": card.id,
                "reason": "compiled aura is missing required source parameters",
            })
            continue
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
