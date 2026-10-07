from __future__ import annotations

import argparse
import difflib
import json
import logging
from pathlib import Path
import sys

from universal_mechanic_inventory import ROOT, build_payload, render_markdown

JSON_OUTPUT = ROOT / "data" / "universal_mechanic_inventory_v1.json"
MD_OUTPUT = ROOT / "docs" / "UNIVERSAL_MECHANIC_INVENTORY.md"
logger = logging.getLogger(__name__)


def write_or_check(path: Path, rendered: str, check: bool) -> bool:
    try:
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        if check and current != rendered:
            print(f"Universal mechanic inventory is stale: {path.relative_to(ROOT)}", file=sys.stderr)
            print(
                "".join(
                    difflib.unified_diff(
                        current.splitlines(True),
                        rendered.splitlines(True),
                        fromfile="committed",
                        tofile="generated",
                    )
                ),
                file=sys.stderr,
            )
            return False
        if not check:
            path.write_text(rendered, encoding="utf-8")
        return True
    except Exception:
        logger.exception("Failed to write/check universal mechanic inventory: %s", path)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the shared engine/hero/monster mechanic inventory.")
    parser.add_argument("--check", action="store_true", help="Fail if committed inventory outputs are stale.")
    args = parser.parse_args()
    try:
        payload = build_payload()
        json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        markdown = render_markdown(payload)
        ok = write_or_check(JSON_OUTPUT, json_text, args.check)
        ok = write_or_check(MD_OUTPUT, markdown, args.check) and ok
        print(
            f"UNIVERSAL_MECHANIC_INVENTORY engine={len(payload['engine']['capabilities'])} "
            f"hero={len(payload['hero_pregen']['mechanics'])} "
            f"monster_abilities={len(payload['monster_2014']['unresolved_printed_abilities'])}"
        )
        return 0 if ok else 1
    except Exception:
        logger.exception("Universal mechanic inventory export failed.")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
