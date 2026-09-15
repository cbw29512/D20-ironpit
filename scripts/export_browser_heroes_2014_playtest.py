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
DESTINATION = ROOT / "frontend" / "browser-heroes.js"

# These are not final player pregens. They are already-certified 2014 SRD NPC
# stat blocks exposed on the hero side so the shared engine can be tested
# without importing any 2024 class mechanics into the 2014 verification lane.
HARNESS_ROLES = (
    ("veteran", "fighter", "Martial harness"),
    ("scout", "ranger", "Ranged harness"),
    ("acolyte", "cleric", "Divine harness"),
    ("mage", "wizard", "Arcane harness"),
)


def _ready_ids() -> set[str]:
    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if payload.get("ruleset") != "2014":
        raise RuntimeError("2014 hero harness received a non-2014 monster ledger.")
    return {
        row["id"]
        for row in payload.get("monsters", [])
        if row.get("status") == "ready"
    }


def _harness_rows() -> list[dict[str, object]]:
    ready_ids = _ready_ids()
    missing = [source_id for source_id, _, _ in HARNESS_ROLES if source_id not in ready_ids]
    if missing:
        raise RuntimeError(f"2014 test harness requires uncertified sources: {missing}")

    sources = {source.id: source for source in load_catalog_2014()}
    rows: list[dict[str, object]] = []
    for source_id, class_id, class_name in HARNESS_ROLES:
        source = sources.get(source_id)
        if source is None:
            raise RuntimeError(f"Missing 2014 catalog source for test harness: {source_id}")
        template = compile_monster_2014(source)
        if template.ruleset != "2014":
            raise RuntimeError(f"Test harness source compiled as {template.ruleset}: {source_id}")
        row = template_row(_serializable_template(template))
        row["class_id"] = class_id
        row["class_name"] = class_name
        row["level"] = 1
        row["build_id"] = "2014-srd-test-harness"
        row["ruleset"] = "2014"
        row["test_harness"] = True
        row["creature_type"] = template.creature_type
        _attach_source_fingerprint(row, template)
        _attach_monster_actions(row, template)
        rows.append(row)
    return rows


def render() -> str:
    try:
        rows = _harness_rows()
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from ledger-certified D&D 5e 2014 SRD test-harness stat blocks. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  const heroes = {payload};\n"
            "  window.IRON_PIT_BROWSER_HEROES = Object.fromEntries(heroes.map((item) => [item.id, item]));\n"
            "  window.IRON_PIT_HERO_RULESET = \"2014\";\n"
            "  window.IRON_PIT_HERO_SCOPE = \"srd-test-harness\";\n"
            f"  window.IRON_PIT_CERTIFIED_HARNESS_COUNT = {len(rows)};\n"
            "})();\n"
        )
    except Exception:
        logger.exception("2014 SRD hero-side test harness rendering failed.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported pure 2014 SRD test harness to %s.", DESTINATION)
    except Exception:
        logger.exception("2014 SRD test harness export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
