from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.monster_forced_displacement_2014 import forced_displacement_inventory_2014
from app.content.monster_source_2014 import load_monster_source_2014

DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "FORCED_DISPLACEMENT_2014.json"


def render() -> str:
    report = forced_displacement_inventory_2014(load_monster_source_2014())
    if report["source_card_count"] != 327:
        raise RuntimeError("Expected the immutable 327-card 2014 source roster.")
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


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
