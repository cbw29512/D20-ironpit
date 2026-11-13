"""Export source-derived 2014 Wanted posters; never maintain a second roster."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-wanted-2014.js"


def blocked_rows_2014() -> list[dict[str, object]]:
    """Recalculate posters from the same source gate that admits combatants."""
    try:
        source = load_monster_source_2014()
        if len(source) != 327:
            raise ValueError("2014 Wanted export requires the pinned 327-card corpus.")
        rows: list[dict[str, object]] = []
        for monster in source:
            blockers = basic_blockers_2014(monster)
            if not blockers:
                continue
            rows.append({
                "id": f"2014-{monster.id}",
                "name": monster.name,
                "challenge_rating": monster.challenge_rating or "?",
                "creature_type": monster.creature_type,
                "blockers": list(blockers),
            })
        rows.sort(key=lambda row: (str(row["name"]).casefold(), str(row["id"])))
        if len({str(row["id"]) for row in rows}) != len(rows):
            raise ValueError("Duplicate source IDs in 2014 Wanted catalog.")
        logger.info("Derived %d Wanted posters from 327 immutable source cards.", len(rows))
        return rows
    except Exception:
        logger.exception("2014 Wanted source classification failed.")
        raise


def render() -> str:
    """Keep every published Wanted row tied to current source classification."""
    try:
        payload = json.dumps(blocked_rows_2014(), separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from 2014 source blockers; do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  window.IRON_PIT_BROWSER_WANTED_2014 = {payload};\n"
            "})();\n"
        )
    except Exception:
        logger.exception("2014 Wanted export rendering failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Wrote derived Wanted board to %s", DESTINATION)
    except Exception:
        logger.exception("Writing generated Wanted board failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
