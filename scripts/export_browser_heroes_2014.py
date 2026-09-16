from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.certified_heroes_2014 import build_certified_hero_entries_2014
from export_browser_heroes import _template

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-heroes-2014.js"


def render() -> str:
    try:
        rows = []
        for (ruleset, class_id, level, build_id), template in build_certified_hero_entries_2014():
            if ruleset != "2014" or template.ruleset != "2014":
                raise ValueError(f"2014 browser hero export crossed ruleset boundary at {template.id}.")
            rows.append(_template((class_id, level, build_id), template))
        if len(rows) != 10:
            raise ValueError(f"Expected ten certified 2014 Fighter levels; found {len(rows)}.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from audited Python 2014 RAW-ready hero templates. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const heroes = {payload};\n"
            "  window.IRON_PIT_BROWSER_HEROES_2014 = Object.fromEntries(heroes.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_2014_HEROES_READY = true;\n"
            "})();\n"
        )
    except Exception:
        logger.exception("Certified 2014 browser hero render failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified 2014 browser heroes to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified 2014 browser hero export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
