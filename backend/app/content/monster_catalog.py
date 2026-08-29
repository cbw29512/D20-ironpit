from __future__ import annotations

import json
from pathlib import Path

from app.domain.catalog import CoverageStatus, MonsterCatalogCard

_DATA_DIR = Path(__file__).with_name("data")
_DATA_PATH = _DATA_DIR / "srd_5_2_1_monsters.json"
_CORRECTIONS_PATH = _DATA_DIR / "srd_5_2_1_monster_corrections.json"

# Ready means every mechanic capable of changing a standard flat-arena fight is
# represented. Terrain-only movement and deliberately unused flee/retreat options
# do not block readiness under docs/ARENA_POLICY.md.
_READY_BY_NAME = {
    "Awakened Shrub": "srd-awakened-shrub",
    "Axe Beak": "srd-axe-beak",
    "Baboon": "srd-baboon",
    "Badger": "srd-badger",
    "Bandit": "srd-bandit",
    "Bat": "srd-bat",
    "Black Bear": "srd-black-bear",
    "Boar": "srd-boar",
    "Brown Bear": "srd-brown-bear",
    "Camel": "srd-camel",
    "Cat": "srd-cat",
    "Commoner": "srd-commoner",
    "Constrictor Snake": "srd-constrictor-snake",
    "Crab": "srd-crab",
    "Crocodile": "srd-crocodile",
    "Deer": "srd-deer",
    "Dire Wolf": "srd-dire-wolf",
    "Draft Horse": "srd-draft-horse",
    "Eagle": "srd-eagle",
    "Elk": "srd-elk",
    "Frog": "srd-frog",
    "Giant Badger": "srd-giant-badger",
    "Giant Bat": "srd-giant-bat",
    "Giant Boar": "srd-giant-boar",
    "Giant Centipede": "srd-giant-centipede",
    "Giant Crab": "srd-giant-crab",
    "Giant Fire Beetle": "srd-giant-fire-beetle",
    "Giant Goat": "srd-giant-goat",
    "Giant Lizard": "srd-giant-lizard",
    "Giant Owl": "srd-giant-owl",
    "Giant Rat": "srd-giant-rat",
    "Giant Weasel": "srd-giant-weasel",
    "Goblin Warrior": "srd-goblin-warrior",
    "Guard": "srd-guard",
    "Hawk": "srd-hawk",
    "Hyena": "srd-hyena",
    "Lizard": "srd-lizard",
    "Mastiff": "srd-mastiff",
    "Mule": "srd-mule",
    "Ogre": "srd-ogre",
    "Owl": "srd-owl",
    "Owlbear": "srd-owlbear",
    "Panther": "srd-panther",
    "Plesiosaurus": "srd-plesiosaurus",
    "Polar Bear": "srd-polar-bear",
    "Pony": "srd-pony",
    "Pteranodon": "srd-pteranodon",
    "Rat": "srd-rat",
    "Raven": "srd-raven",
    "Rhinoceros": "srd-rhinoceros",
    "Riding Horse": "srd-riding-horse",
    "Saber-Toothed Tiger": "srd-saber-toothed-tiger",
    "Scout": "srd-scout",
    "Tiger": "srd-tiger",
    "Vulture": "srd-vulture",
    "Warhorse": "srd-warhorse",
    "Warrior Infantry": "srd-warrior-infantry",
    "Weasel": "srd-weasel",
    "Wolf": "srd-wolf",
}


def load_monster_rows() -> list[dict[str, object]]:
    rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    corrections = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("Vended parser output must contain its known 328 base records.")
    if not isinstance(corrections, list) or len(corrections) != 2:
        raise RuntimeError("SRD correction layer must restore exactly two swallowed records.")
    combined = [*rows, *corrections]
    ids = {str(row["id"]) for row in combined}
    names = {str(row["name"]) for row in combined}
    if len(combined) != 330 or len(ids) != 330 or len(names) != 330:
        raise RuntimeError("SRD 5.2.1 monster catalog must contain 330 unique creatures.")
    return combined


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
    return [_card(row) for row in load_monster_rows()]
