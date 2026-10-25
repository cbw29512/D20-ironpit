"""Generate the durable 327-card Death Trigger coverage report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "DEATH_TRIGGER_BINDINGS_2014.json"

from app.content.monster_death_triggers_2014 import (
    death_trigger_actions_2014,
    semantic_death_trigger_names_2014,
    supports_death_triggers_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, complete, wired, structured, exceptions = [], [], [], [], []
    for card in cards:
        semantic_names = list(semantic_death_trigger_names_2014(card))
        if not card.death_trigger_actions and not semantic_names:
            continue
        applicable.append(card.id)
        if card.death_trigger_actions:
            structured.append(card.id)
        actions = death_trigger_actions_2014(card)
        if actions:
            complete.append(card.id)
        if actions and supports_death_triggers_2014(card):
            wired.append(card.id)
        else:
            exceptions.append({
                "monster": card.id,
                "semantic_traits": semantic_names,
                "reason": (
                    "printed Death Trigger is not representable by the shared "
                    "save/damage/timed-effect schema"
                    if not card.death_trigger_actions
                    else "structured action is incompatible with the shared save/damage schema"
                ),
            })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "structured_source_card_count": len(structured),
        "source_declared_card_count": len(complete),
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "wired_cards": wired,
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "cards_with_death_trigger_actions": len(structured),
        "death_effect_dispatch_wired": len(wired),
        "status": "complete" if not exceptions else "partial: exceptions require schema support",
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
