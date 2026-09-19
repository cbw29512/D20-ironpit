from __future__ import annotations

import json
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "monster_certification_manifest.json"


def test_durable_monster_manifest_matches_live_raw_ready_catalog() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_ready = {
        row["runtime_template_id"]
        for row in payload["monsters"]
        if row["public_ready_status"] == "ready"
    }
    catalog_ready = {
        card.runnable_template_id
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }

    assert None not in manifest_ready
    assert None not in catalog_ready
    assert manifest_ready == catalog_ready
    assert payload["summary"]["public_ready"] == len(catalog_ready)
