from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014
from browser_template_serializer import template_row
from export_browser_monsters import (
    _attach_monster_actions,
    _attach_source_fingerprint,
    _serializable_template,
)

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data" / "monsters" / "2014" / "certification_ledger.json"
DESTINATION = ROOT / "frontend" / "browser-monsters-generated.js"


def _ledger_ready_ids() -> tuple[set[str], int]:
    try:
        payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        if payload.get("ruleset") != "2014":
            raise RuntimeError("2014 playtest exporter received a non-2014 ledger.")
        ready_ids = {
            row["id"]
            for row in payload.get("monsters", [])
            if row.get("status") == "ready"
        }
        ready_count = int(payload.get("ready_count", -1))
        if len(ready_ids) != ready_count:
            raise RuntimeError("2014 ledger ready_count does not match ready monster rows.")
        return ready_ids, ready_count
    except Exception:
        logger.exception("Failed to read the 2014 certification ledger.")
        raise


def _certified_monsters():
    try:
        ready_ids, ready_count = _ledger_ready_ids()
        sources = load_catalog_2014()
        source_ids = {source.id for source in sources}
        missing = ready_ids - source_ids
        if missing:
            raise RuntimeError(f"2014 ledger references missing catalog ids: {sorted(missing)}")
        monsters = [compile_monster_2014(source) for source in sources if source.id in ready_ids]
        if len(monsters) != ready_count:
            raise RuntimeError(
                f"2014 browser export compiled {len(monsters)} monsters; ledger requires {ready_count}."
            )
        return monsters
    except Exception:
        logger.exception("Failed to compile the certified 2014 browser roster.")
        raise


def render() -> str:
    try:
        rows = []
        for template in _certified_monsters():
            row = template_row(_serializable_template(template))
            row["creature_type"] = template.creature_type
            _attach_source_fingerprint(row, template)
            _attach_monster_actions(row, template)
            rows.append(row)
        ids = {row["id"] for row in rows}
        if len(ids) != len(rows):
            raise RuntimeError("2014 browser monster export contains duplicate template IDs.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from ledger-certified D&D 5e 2014 monster templates. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const monsters = {payload};\n"
            "  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_CANONICAL_MONSTERS_READY = true;\n"
            "  window.IRON_PIT_RULESET = \"2014\";\n"
            f"  window.IRON_PIT_CERTIFIED_MONSTER_COUNT = {len(rows)};\n"
            "})();\n"
        )
    except Exception:
        logger.exception("2014 certified browser monster rendering failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified 2014 browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("2014 certified browser monster export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
