from __future__ import annotations

import json
from pathlib import Path

from app.domain.catalog import CoverageStatus, MonsterCatalogCard

_DATA_PATH = Path(__file__).with_name("data") / "srd_5_2_1_monsters.json"

# Only monsters whose combat-relevant stat-block behavior is fully represented by
# the current arena engine belong here. Everything else remains browsable but
# fails closed until its missing mechanics are certified.
_READY_BY_NAME = {
    "Axe Beak": "srd-axe-beak",
    "Bandit": "srd-bandit",
    "Guard": "srd-guard",
}

_BLOCKERS_BY_NAME = {
    "Commoner": ["training-ability-check-trait-not-modeled"],
    "Giant Lizard": ["climb-speed-and-spider-climb-not-modeled"],
    "Giant Rat": ["pack-tactics-target-adjacency-not-modeled-raw", "climb-speed-not-modeled"],
    "Giant Weasel": ["climb-speed-not-modeled"],
    "Goblin Warrior": ["nimble-escape-not-modeled"],
}


def _load_rows() -> list[dict[str, object]]:
    rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("SRD 5.2.1 monster catalog must contain exactly 328 records.")
    return rows


def _card(row: dict[str, object]) -> MonsterCatalogCard:
    name = str(row["name"])
    template_id = _READY_BY_NAME.get(name)
    blockers = _BLOCKERS_BY_NAME.get(name, ["monster-combat-mechanics-not-certified"])
    return MonsterCatalogCard(
        id=str(row["id"]),
        name=name,
        challenge_rating=str(row["challenge"]),
        monster_type=str(row["type"]),
        armor_class=str(row["armorClass"]),
        hit_points=str(row["hitPoints"]),
        speed=str(row["speed"]),
        source_page=int(row["sourcePage"]),
        source_reference=str(row["sourceReference"]),
        coverage_status=(CoverageStatus.RAW_READY if template_id else CoverageStatus.BLOCKED),
        runnable_template_id=template_id,
        blockers=[] if template_id else blockers,
    )


def build_monster_catalog() -> list[MonsterCatalogCard]:
    return [_card(row) for row in _load_rows()]
