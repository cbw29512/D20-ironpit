from __future__ import annotations

import logging
from collections.abc import Callable

from app.content.barbarian import build_demo_barbarian
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.low_cr_monsters import build_bandit, build_guard
from app.content.rogue import build_demo_rogue
from app.domain.models import CombatantTemplate, DuelMode

logger = logging.getLogger(__name__)
Builder = Callable[[], CombatantTemplate]

CHARACTER_BUILDERS: dict[str, Builder] = {
    "aldric-vane-l1": build_demo_fighter,
    "mara-vale-l1": build_demo_rogue,
    "kara-stonefury-l1": build_demo_barbarian,
}
MONSTER_BUILDERS: dict[str, Builder] = {
    "srd-goblin-warrior": build_goblin_warrior,
    "srd-bandit": build_bandit,
    "srd-guard": build_guard,
}
PUBLIC_MONSTER_IDS = ("srd-bandit", "srd-guard")
MONSTER_STARTING_DISTANCES: dict[str, int] = {
    "srd-goblin-warrior": 20,
    "srd-bandit": 20,
    "srd-guard": 5,
}


def build_test_catalog() -> dict[str, list[CombatantTemplate]]:
    try:
        return {
            "characters": [builder() for builder in CHARACTER_BUILDERS.values()],
            "monsters": [MONSTER_BUILDERS[item_id]() for item_id in PUBLIC_MONSTER_IDS],
        }
    except Exception as exc:
        logger.exception("Failed to build test roster catalog.")
        raise RuntimeError("Test roster catalog could not be created.") from exc


def build_test_character(character_id: str) -> CombatantTemplate:
    try:
        builder = CHARACTER_BUILDERS.get(character_id)
        if builder is None:
            raise ValueError(f"Unknown character: {character_id}")
        return builder()
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build test character %s.", character_id)
        raise RuntimeError("Test character could not be created.") from exc


def build_test_monster(monster_id: str) -> CombatantTemplate:
    try:
        builder = MONSTER_BUILDERS.get(monster_id)
        if builder is None:
            raise ValueError(f"Unknown monster: {monster_id}")
        return builder()
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build test monster %s.", monster_id)
        raise RuntimeError("Test monster could not be created.") from exc


def get_monster_opening_mode(monster_id: str) -> DuelMode:
    if monster_id not in MONSTER_BUILDERS:
        raise ValueError(f"Unknown monster: {monster_id}")
    return DuelMode.CLOSE


def get_monster_starting_distance(monster_id: str) -> int:
    try:
        return MONSTER_STARTING_DISTANCES[monster_id]
    except KeyError as exc:
        raise ValueError(f"No arena opening distance for monster: {monster_id}") from exc
