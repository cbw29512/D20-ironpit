from __future__ import annotations


def _checked_level(level: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    return level


def proficiency_bonus(level: int) -> int:
    level = _checked_level(level)
    return 2 + (level - 1) // 4


def fixed_class_hit_points(level: int, hit_die_size: int, constitution_modifier: int) -> int:
    """RAW fixed-HP option: max Hit Die at level 1, fixed average thereafter."""
    level = _checked_level(level)
    if hit_die_size not in (6, 8, 10, 12):
        raise ValueError("Class Hit Die must be d6, d8, d10, or d12.")
    first = max(1, hit_die_size + constitution_modifier)
    later = max(1, hit_die_size // 2 + 1 + constitution_modifier)
    return first + (level - 1) * later


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


def cleric_channel_divinity_uses(level: int) -> int:
    """2024 Cleric Channel Divinity uses; feature begins at level 2."""
    level = _checked_level(level)
    if level < 2:
        return 0
    if level < 6:
        return 2
    if level < 18:
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


def fighter_action_surge_uses(level: int) -> int:
    """2024 Fighter Action Surge uses; level 17 grants a second use."""
    level = _checked_level(level)
    if level < 2:
        return 0
    return 2 if level >= 17 else 1


def fighter_indomitable_uses(level: int) -> int:
    """2024 Fighter Indomitable uses; feature begins at level 9."""
    level = _checked_level(level)
    if level < 9:
        return 0
    if level < 13:
        return 1
    if level < 17:
        return 2
    return 3


def orc_adrenaline_rush_uses(level: int) -> int:
    """2024 Orc Adrenaline Rush uses equal the character's Proficiency Bonus."""
    return proficiency_bonus(level)
