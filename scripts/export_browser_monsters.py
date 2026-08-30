from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.roster import build_arena_roster
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-generated.js"


def render() -> str:
    try:
        monsters = build_arena_roster().monsters
        rows = [template_row(template) for template in monsters]
        ids = {row["id"] for row in rows}
        if len(rows) != len(ids):
            raise RuntimeError("Certified browser monster export contains duplicate template IDs.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from canonical Python RAW-ready monster templates. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const monsters = {payload};\n"
            "  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
            "})();\n"
        )
    except Exception:
        logger.exception("Certified browser monster rendering failed.")
        raise


def main() -> None:
    try:
        content = render()
        DESTINATION.write_text(content, encoding="utf-8")
        logger.info("Exported canonical browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
