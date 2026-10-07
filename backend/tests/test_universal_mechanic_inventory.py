from __future__ import annotations

import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "data" / "universal_mechanic_inventory_v1.json"
logger = logging.getLogger(__name__)


def _load_inventory() -> dict[str, object]:
    try:
        return json.loads(INVENTORY.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed to load universal mechanic inventory.")
        raise


def test_universal_mechanic_inventory_has_unique_engine_and_hero_ids() -> None:
    payload = _load_inventory()
    engine_ids = [item["id"] for item in payload["engine"]["capabilities"]]
    hero_ids = [item["id"] for item in payload["hero_pregen"]["mechanics"]]
    assert len(engine_ids) == len(set(engine_ids))
    assert len(hero_ids) == len(set(hero_ids))
    assert payload["hero_pregen"]["roster"] == {"classes": 12, "subclasses": 37}


def test_monster_reverse_index_is_unique_sorted_and_counted() -> None:
    payload = _load_inventory()
    abilities = payload["monster_2014"]["unresolved_printed_abilities"]
    names = [item["printed_name"] for item in abilities]
    assert names == sorted(names)
    assert len(names) == len(set(names))
    for item in abilities:
        assert item["monsters"] == sorted(set(item["monsters"]))
        assert item["demand_count"] == len(item["monsters"])


def test_homebrew_lookup_exposes_supported_universal_capability_ids() -> None:
    payload = _load_inventory()
    supported = {
        item["id"]
        for item in payload["engine"]["capabilities"]
        if item["status"] == "supported"
    }
    assert "action-economy" in supported
    assert "saving-throws" in supported
    assert "typed-damage-resistance-immunity-vulnerability" in supported
