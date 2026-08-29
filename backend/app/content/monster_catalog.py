from __future__ import annotations

import json
from pathlib import Path

from app.domain.catalog import CoverageStatus, MonsterCatalogCard

_DATA_PATH = Path(__file__).with_name("data") / "srd_5_2_1_monsters.json"

# Ready means every mechanic capable of changing a standard flat-arena fight is
# represented. Terrain-only movement and deliberately unused flee/retreat options
# do not block readiness under docs/ARENA_POLICY.md.
_READY_BY_NAME = {
    "Axe Beak": "srd-axe-beak",
    "Bandit": "srd-bandit",
    "Black Bear": "srd-black-bear",
    "Brown Bear": "srd-brown-bear",
    "Camel": "srd-camel",
    "Commoner": "srd-commoner",
    "Deer": "srd-deer",
    "Dire Wolf": "srd-dire-wolf",
    "Draft Horse": "srd-draft-horse",
    "Giant Badger": "srd-giant-badger",
    "Giant Lizard": "srd-giant-lizard",
    "Giant Rat": "srd-giant-rat",
    "Giant Weasel": "srd-giant-weasel",
    "Goblin Warrior": "srd-goblin-warrior",
    "Guard": "srd-guard",
    "Wolf": "srd-wolf",
}


def _load_rows() -> list[dict[str, object]]:
    rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("SRD 5.2.1 monster catalog must contain exactly 328 records.")
    return rows


def _card(row: dict[str, object]) -> MonsterCatalogCard:
    name = str(row["name"])
    template_id = _READY_BY_NAME.get(name)
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
        blockers=[] if template_id else ["monster-combat-mechanics-not-certified"],
    )


def build_monster_catalog() -> list[MonsterCatalogCard]:
    return [_card(row) for row in _load_rows()]
