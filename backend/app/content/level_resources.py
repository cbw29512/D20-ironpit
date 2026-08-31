from __future__ import annotations


def _checked_level(level: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    return level


def proficiency_bonus(level: int) -> int:
    level = _checked_level(level)
    return 2 + (level - 1) // 4


def barbarian_rage_uses(level: int) -> int:
    """2024 Barbarian Rage uses available when a fresh fight begins."""
    level = _checked_level(level)
    if level <= 2:
        return 2
    if level <= 5:
        return 3
    if level <= 11:
        return 4
    if level <= 16:
        return 5
    return 6


def barbarian_rage_damage_bonus(level: int) -> int:
    level = _checked_level(level)
    if level <= 8:
        return 2
    if level <= 15:
        return 3
    return 4


def fighter_second_wind_uses(level: int) -> int:
    """2024 Fighter Second Wind uses available when a fresh fight begins."""
    level = _checked_level(level)
    if level <= 3:
        return 2
    if level <= 9:
        return 3
    return 4


def orc_adrenaline_rush_uses(level: int) -> int:
    """2024 Orc Adrenaline Rush uses equal the character's Proficiency Bonus."""
    return proficiency_bonus(level)
