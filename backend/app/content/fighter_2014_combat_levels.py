from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Fighter2014CombatLevel:
    level: int
    proficiency_bonus: int
    max_hp: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    attack_count: int
    second_wind_uses: int
    action_surge_uses: int
    indomitable_uses: int
    critical_hit_minimum: int
    remarkable_athlete: bool
    fighting_styles: tuple[str, ...]
    source: str


_SOURCE = "D&D Beyond Basic Rules 2014: Fighter and Champion"

FIGHTER_2014_COMBAT_LEVELS: dict[int, Fighter2014CombatLevel] = {
    1: Fighter2014CombatLevel(1, 2, 13, 16, 14, 16, 11, 11, 9, 1, 1, 0, 0, 20, False, ("Defense",), _SOURCE),
    2: Fighter2014CombatLevel(2, 2, 22, 16, 14, 16, 11, 11, 9, 1, 1, 1, 0, 20, False, ("Defense",), _SOURCE),
    3: Fighter2014CombatLevel(3, 2, 31, 16, 14, 16, 11, 11, 9, 1, 1, 1, 0, 19, False, ("Defense",), _SOURCE),
    4: Fighter2014CombatLevel(4, 2, 40, 18, 14, 16, 11, 11, 9, 1, 1, 1, 0, 19, False, ("Defense",), _SOURCE),
    5: Fighter2014CombatLevel(5, 3, 49, 18, 14, 16, 11, 11, 9, 2, 1, 1, 0, 19, False, ("Defense",), _SOURCE),
    6: Fighter2014CombatLevel(6, 3, 58, 20, 14, 16, 11, 11, 9, 2, 1, 1, 0, 19, False, ("Defense",), _SOURCE),
    7: Fighter2014CombatLevel(7, 3, 67, 20, 14, 16, 11, 11, 9, 2, 1, 1, 0, 19, True, ("Defense",), _SOURCE),
    8: Fighter2014CombatLevel(8, 3, 84, 20, 14, 18, 11, 11, 9, 2, 1, 1, 0, 19, True, ("Defense",), _SOURCE),
    9: Fighter2014CombatLevel(9, 4, 94, 20, 14, 18, 11, 11, 9, 2, 1, 1, 1, 19, True, ("Defense",), _SOURCE),
    10: Fighter2014CombatLevel(10, 4, 104, 20, 14, 18, 11, 11, 9, 2, 1, 1, 1, 19, True, ("Defense", "Archery"), _SOURCE),
}


def fighter_2014_level(level: int) -> Fighter2014CombatLevel:
    try:
        return FIGHTER_2014_COMBAT_LEVELS[level]
    except KeyError as exc:
        logger.exception("Unsupported 2014 Fighter level %s.", level)
        raise ValueError("2014 Champion Fighter certification currently covers levels 1 through 10.") from exc
