from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.monster_neighbor_bleed_corrections import apply_neighbor_bleed_corrections
from app.content.monster_neighbor_bleed_normalizer import normalize_neighbor_name_bleed
from app.content.monster_section_heading_corrections import apply_section_heading_corrections
from app.domain.catalog import CoverageStatus, MonsterCatalogCard
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).with_name("data")
_DATA_PATH = _DATA_DIR / "srd_5_2_1_monsters.json"
_CORRECTIONS_PATH = _DATA_DIR / "srd_5_2_1_monster_corrections.json"

# Candidate means combat mechanics are implemented. Final RAW READY status is
# granted only after the runtime template passes the complete source audit.
_READY_BY_NAME = {
    "Ankylosaurus": "srd-ankylosaurus", "Archelon": "srd-archelon",
    "Awakened Shrub": "srd-awakened-shrub", "Axe Beak": "srd-axe-beak", "Baboon": "srd-baboon",
    "Badger": "srd-badger", "Bandit": "srd-bandit", "Bandit Captain": "srd-bandit-captain",
    "Bat": "srd-bat", "Black Bear": "srd-black-bear", "Blood Hawk": "srd-blood-hawk", "Boar": "srd-boar", "Brown Bear": "srd-brown-bear",
    "Camel": "srd-camel", "Cat": "srd-cat", "Commoner": "srd-commoner", "Constrictor Snake": "srd-constrictor-snake",
    "Crab": "srd-crab", "Crocodile": "srd-crocodile", "Deer": "srd-deer", "Dire Wolf": "srd-dire-wolf",
    "Draft Horse": "srd-draft-horse", "Eagle": "srd-eagle", "Elk": "srd-elk", "Frog": "srd-frog",
    "Giant Badger": "srd-giant-badger", "Giant Bat": "srd-giant-bat", "Giant Boar": "srd-giant-boar",
    "Giant Centipede": "srd-giant-centipede", "Giant Constrictor Snake": "srd-giant-constrictor-snake",
    "Giant Crab": "srd-giant-crab", "Giant Crocodile": "srd-giant-crocodile",
    "Giant Eagle": "srd-giant-eagle", "Giant Elk": "srd-giant-elk",
    "Giant Fire Beetle": "srd-giant-fire-beetle", "Giant Goat": "srd-giant-goat",
    "Giant Lizard": "srd-giant-lizard", "Giant Owl": "srd-giant-owl",
    "Giant Rat": "srd-giant-rat", "Giant Venomous Snake": "srd-giant-venomous-snake",
    "Giant Wasp": "srd-giant-wasp", "Giant Weasel": "srd-giant-weasel",
    "Giant Wolf Spider": "srd-giant-wolf-spider", "Goblin Boss": "srd-goblin-boss",
    "Goblin Minion": "srd-goblin-minion", "Goblin Warrior": "srd-goblin-warrior", "Guard": "srd-guard", "Hawk": "srd-hawk",
    "Hippogriff": "srd-hippogriff", "Hobgoblin Warrior": "srd-hobgoblin-warrior", "Hyena": "srd-hyena",
    "Jackal": "srd-jackal", "Knight": "srd-knight", "Kobold Warrior": "srd-kobold-warrior", "Lizard": "srd-lizard",
    "Mastiff": "srd-mastiff", "Mule": "srd-mule", "Noble": "srd-noble", "Ogre": "srd-ogre", "Owl": "srd-owl",
    "Owlbear": "srd-owlbear", "Panther": "srd-panther", "Plesiosaurus": "srd-plesiosaurus",
    "Polar Bear": "srd-polar-bear", "Pony": "srd-pony", "Pteranodon": "srd-pteranodon",
    "Rat": "srd-rat", "Raven": "srd-raven", "Rhinoceros": "srd-rhinoceros",
    "Riding Horse": "srd-riding-horse", "Saber-Toothed Tiger": "srd-saber-toothed-tiger",
    "Scout": "srd-scout", "Tiger": "srd-tiger", "Tyrannosaurus Rex": "srd-tyrannosaurus-rex",
    "Vulture": "srd-vulture", "Warhorse": "srd-warhorse", "Warrior Infantry": "srd-warrior-infantry",
    "Warrior Veteran": "srd-warrior-veteran", "Weasel": "srd-weasel", "Wolf": "srd-wolf",
    "Animated Armor": "srd-animated-armor", "Animated Flying Sword": "srd-animated-flying-sword",
    "Awakened Tree": "srd-awakened-tree", "Flying Snake": "srd-flying-snake",
    "Gargoyle": "srd-gargoyle", "Grimlock": "srd-grimlock", "Guard Captain": "srd-guard-captain",
    "Hippopotamus": "srd-hippopotamus", "Killer Whale": "srd-killer-whale",
    "Manticore": "srd-manticore", "Pegasus": "srd-pegasus", "Scorpion": "srd-scorpion",
    "Skeleton": "srd-skeleton", "Spider": "srd-spider", "Tough": "srd-tough",
    "Venomous Snake": "srd-venomous-snake", "Violet Fungus": "srd-violet-fungus",
}


@lru_cache(maxsize=1)
def _canonical_monster_rows() -> tuple[dict[str, object], ...]:
    rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    corrections = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("Vended parser output must contain its known 328 base records.")
    if not isinstance(corrections, list) or len(corrections) != 3:
        raise RuntimeError("SRD correction layer must contain one replacement and two restored records.")
    correction_by_id = {str(row["id"]): row for row in corrections}
    if len(correction_by_id) != 3:
        raise RuntimeError("SRD correction records must have unique ids.")
    base_ids = {str(row["id"]) for row in rows}
    replacements = [row for row in corrections if str(row["id"]) in base_ids]
    additions = [row for row in corrections if str(row["id"]) not in base_ids]
    if len(replacements) != 1 or len(additions) != 2:
        raise RuntimeError("SRD correction layer must replace one row and restore two swallowed rows.")
    combined = [correction_by_id.get(str(row["id"]), row) for row in rows] + additions
    combined = apply_neighbor_bleed_corrections(combined)
    combined = normalize_neighbor_name_bleed(combined)
    combined = apply_section_heading_corrections(combined)
    ids = {str(row["id"]) for row in combined}
    names = {str(row["name"]) for row in combined}
    if len(combined) != 330 or len(ids) != 330 or len(names) != 330:
        raise RuntimeError("SRD 5.2.1 monster catalog must contain 330 unique creatures.")
    from app.content.monster_source_integrity import validate_monster_source_integrity

    validate_monster_source_integrity(combined)
    return tuple(combined)


def load_monster_rows() -> list[dict[str, object]]:
    """Return mutation-safe copies of the once-validated canonical SRD catalog."""
    return deepcopy(list(_canonical_monster_rows()))


def _runtime_monsters() -> dict[str, CombatantTemplate]:
    try:
        from app.content.roster import build_arena_roster

        return {template.id: template for template in build_arena_roster().monsters}
    except Exception:
        logger.exception("Runtime monster roster failed; RAW READY candidates will fail closed.")
        return {}


def _card(row: dict[str, object], runtime: dict[str, CombatantTemplate]) -> MonsterCatalogCard:
    name = str(row["name"])
    candidate_id = _READY_BY_NAME.get(name)
    blockers = [] if candidate_id else ["monster-combat-mechanics-not-certified"]
    if candidate_id:
        template = runtime.get(candidate_id)
        if template is None:
            blockers = ["missing-runtime-template"]
        else:
            try:
                from app.content.monster_source_audit import audit_monster_source

                blockers = audit_monster_source(template, row)
            except Exception:
                logger.exception("Full SRD certification failed for %s.", name)
                blockers = ["monster-source-audit-failed"]
    raw_ready = bool(candidate_id and not blockers)
    return MonsterCatalogCard(
        id=str(row["id"]), name=name, challenge_rating=str(row["challenge"]), monster_type=str(row["type"]),
        armor_class=str(row["armorClass"]), hit_points=str(row["hitPoints"]), speed=str(row["speed"]),
        source_page=int(row["sourcePage"]), source_reference=str(row["sourceReference"]),
        coverage_status=CoverageStatus.RAW_READY if raw_ready else CoverageStatus.BLOCKED,
        runnable_template_id=candidate_id if raw_ready else None,
        blockers=blockers,
    )


def build_monster_catalog() -> list[MonsterCatalogCard]:
    runtime = _runtime_monsters()
    return [_card(row, runtime) for row in load_monster_rows()]
