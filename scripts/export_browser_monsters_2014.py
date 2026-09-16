from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_capabilities_2014 import build_2014_mvp_monsters
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-2014.js"
_EXPECTED_IDS = {"2014-goblin", "2014-bandit", "2014-skeleton", "2014-brown-bear"}


def render() -> str:
    try:
        rows = [template_row(template) for template in build_2014_mvp_monsters()]
        ids = {row["id"] for row in rows}
        if ids != _EXPECTED_IDS or len(rows) != len(ids):
            raise RuntimeError("2014 browser MVP export does not match the certified four-monster slice.")
        if any(row.get("ruleset") != "2014" or row.get("kind") != "monster" for row in rows):
            raise RuntimeError("2014 browser MVP export contains a non-2014 monster.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from the certified isolated 2014 MVP monster templates. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const monsters = {payload};\n"
            "  window.IRON_PIT_BROWSER_MONSTERS_2014 = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_2014_MVP_READY = true;\n"
            "})();\n"
        )
    except Exception:
        logger.exception("2014 browser MVP monster rendering failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified 2014 MVP browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("2014 browser MVP monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
