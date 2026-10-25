"""Generate the 327-card staged-disease coverage report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "STAGED_DISEASE_BINDINGS_2014.json"

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_staged_disease_2014 import staged_disease_candidates_2014


def report() -> dict:
    cards = load_monster_source_2014()
    applicable = [card.id for card in staged_disease_candidates_2014(cards)]
    exceptions = [{
        "monster": card_id,
        "reason": (
            "removal capability is representable, but the source attack still requires "
            "generic 10-round activation plus 100-round acid/moisture lifecycle"
        ),
    } for card_id in applicable]
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "removal_contract_card_count": len(applicable),
        "wired_python_card_count": 0,
        "wired_browser_card_count": 0,
        "wired_cards": [],
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "partial: exact staged lifecycle still required",
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
