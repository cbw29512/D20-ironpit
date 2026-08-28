from __future__ import annotations

import logging
from collections.abc import Callable

from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.low_cr_monsters import build_bandit, build_guard
from app.content.rogue import build_demo_rogue
from app.domain.models import CombatantTemplate, DuelMode

logger = logging.getLogger(__name__)
Builder = Callable[[], CombatantTemplate]

CHARACTER_BUILDERS: dict[str, Builder] = {
    "aldric-vane-l1": build_demo_fighter,
    "mara-vale-l1": build_demo_rogue,
}
MONSTER_BUILDERS: dict[str, Builder] = {
    "srd-goblin-warrior": build_goblin_warrior,
    "srd-bandit": build_bandit,
    "srd-guard": build_guard,
}
MONSTER_OPENING_MODES: dict[str, DuelMode] = {
    "srd-goblin-warrior": DuelMode.RANGED,
    "srd-bandit": DuelMode.RANGED,
    "srd-guard": DuelMode.MELEE,
}


def build_test_catalog() -> dict[str, list[CombatantTemplate]]:
    try:
        return {
            "characters": [builder() for builder in CHARACTER_BUILDERS.values()],
            "monsters": [builder() for builder in MONSTER_BUILDERS.values()],
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
    try:
        mode = MONSTER_OPENING_MODES.get(monster_id)
        if mode is None:
            raise ValueError(f"No arena opening policy for monster: {monster_id}")
        return mode
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve arena opening mode for %s.", monster_id)
        raise RuntimeError("Monster opening mode could not be resolved.") from exc
