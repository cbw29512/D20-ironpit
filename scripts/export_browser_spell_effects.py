from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.spell_effects import SHIELD_OF_FAITH
from browser_template_serializer import defense_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-spell-effects.js"


def render() -> str:
    rows = [defense_row(SHIELD_OF_FAITH)]
    payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    return (
        "/* GENERATED from canonical Python certified spell effects. Do not hand-edit. */\n"
        "(() => {\n  \"use strict\";\n"
        f"  const spells = {payload};\n"
        "  window.IRON_PIT_BROWSER_SPELL_EFFECTS = Object.fromEntries(spells.map((item) => [item.id, item]));\n"
        "})();\n"
    )


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified browser spell effects to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser spell-effect export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
